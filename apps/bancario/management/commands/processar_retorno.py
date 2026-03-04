"""
Uso:
    python manage.py processar_retorno --importacao-id=42
    python manage.py processar_retorno --importacao-id=42 --dry-run

Agendamento (pode ser chamado via signal ao salvar ArquivoRetorno):
    from django.db.models.signals import post_save
    @receiver(post_save, sender=ArquivoRetorno)
    def auto_processar(sender, instance, created, **kwargs):
        if created:
            call_command("processar_retorno", importacao_id=instance.pk)
"""

import os
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.bancario.models import (
    ImportacaoExtrato, MovimentoBancario,
    ConciliacaoBancaria, DivergenciaConciliacao,
    StatusConciliacao, TipoMovimentoBancario,
)
from apps.financeiro.models import LancamentoFinanceiro, ContaPagar, ContaReceber


TOLERANCIA_DIAS = 1      # dias de tolerância para match de data
TOLERANCIA_VALOR = Decimal("0.05")  # centavos de tolerância para match de valor


class Command(BaseCommand):
    help = "Processa arquivo de retorno bancário importado e concilia automaticamente."

    def add_arguments(self, parser):
        parser.add_argument("--importacao-id", type=int, required=True,
                            help="PK da ImportacaoExtrato a processar.")
        parser.add_argument("--dry-run", action="store_true",
                            help="Simula sem gravar no banco.")
        parser.add_argument("--forcar", action="store_true",
                            help="Reprocessa mesmo se já foi processado antes.")

    def handle(self, *args, **options):
        importacao_id = options["importacao_id"]
        dry_run = options["dry_run"]
        forcar = options["forcar"]

        try:
            importacao = ImportacaoExtrato.objects.select_related(
                "conta_bancaria", "empresa"
            ).get(pk=importacao_id)
        except ImportacaoExtrato.DoesNotExist:
            raise CommandError(f"ImportacaoExtrato #{importacao_id} não encontrada.")

        if importacao.processado and not forcar:
            self.stdout.write(
                self.style.WARNING(f"Importação #{importacao_id} já foi processada. Use --forcar para reprocessar.")
            )
            return

        self.stdout.write(
            self.style.NOTICE(
                f"[{timezone.now():%Y-%m-%d %H:%M}] Processando importação #{importacao_id} "
                f"| Conta: {importacao.conta_bancaria.nome} | dry_run={dry_run}"
            )
        )

        # Lê e parseia o arquivo
        movimentos_raw = self._parsear_arquivo(importacao)
        if not movimentos_raw:
            self.stdout.write(self.style.ERROR("Nenhum movimento encontrado no arquivo."))
            return

        self.stdout.write(f"  {len(movimentos_raw)} movimento(s) encontrado(s) no arquivo.")

        # Statuses
        status_conciliado, _ = StatusConciliacao.objects.get_or_create(nome="Conciliada")
        status_pendente, _ = StatusConciliacao.objects.get_or_create(nome="Pendente")
        status_divergente, _ = StatusConciliacao.objects.get_or_create(nome="Divergente")

        total_conciliados = 0
        total_divergentes = 0
        log_linhas = []

        for mov_raw in movimentos_raw:
            resultado = self._processar_movimento(
                importacao, mov_raw,
                status_conciliado, status_pendente, status_divergente,
                dry_run,
            )
            if resultado == "conciliado":
                total_conciliados += 1
            else:
                total_divergentes += 1
            log_linhas.append(f"{mov_raw['data']} | {mov_raw['valor']:>15.2f} | {resultado} | {mov_raw['descricao'][:50]}")

        if not dry_run:
            importacao.processado = True
            importacao.total_registros = len(movimentos_raw)
            importacao.total_conciliados = total_conciliados
            importacao.total_divergentes = total_divergentes
            importacao.log_processamento = "\n".join(log_linhas)
            importacao.save(update_fields=[
                "processado", "total_registros",
                "total_conciliados", "total_divergentes",
                "log_processamento",
            ])

        self.stdout.write(
            self.style.SUCCESS(
                f"Concluído: {total_conciliados} conciliados | {total_divergentes} divergentes."
            )
        )

    # ──────────────────────────────────────────────
    # Parser de arquivo
    # ──────────────────────────────────────────────

    def _parsear_arquivo(self, importacao: ImportacaoExtrato) -> list[dict]:
        """
        Parseia o arquivo de extrato. Suporta:
        - OFX (formato SGML/XML simplificado)
        - CNAB (formato posicional — fallback genérico por CSV/TXT)
        - CSV simples (data;valor;descricao)

        Retorna lista de dicts: {data, valor, descricao, documento, natureza}
        """
        try:
            arquivo = importacao.arquivo
            arquivo.seek(0)
            conteudo = arquivo.read().decode("utf-8", errors="replace")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro ao ler arquivo: {e}"))
            return []

        nome = importacao.nome_arquivo.lower()

        if nome.endswith(".ofx"):
            return self._parsear_ofx(conteudo)
        elif nome.endswith(".csv"):
            return self._parsear_csv(conteudo)
        else:
            # Tenta CNAB 240 ou fallback CSV
            return self._parsear_cnab(conteudo) or self._parsear_csv(conteudo)

    def _parsear_ofx(self, conteudo: str) -> list[dict]:
        """Parser simples de OFX (SGML)."""
        import re
        movimentos = []
        transacoes = re.findall(r"<STMTTRN>(.*?)</STMTTRN>", conteudo, re.DOTALL)

        for t in transacoes:
            def tag(nome):
                m = re.search(rf"<{nome}>(.*?)(?:<|$)", t, re.DOTALL)
                return m.group(1).strip() if m else ""

            try:
                trntype = tag("TRNTYPE")
                dtposted = tag("DTPOSTED")[:8]  # YYYYMMDD
                valor_str = tag("TRNAMT").replace(",", ".")
                memo = tag("MEMO") or tag("NAME")
                fitid = tag("FITID")

                data_mov = date(int(dtposted[:4]), int(dtposted[4:6]), int(dtposted[6:8]))
                valor = Decimal(valor_str)
                natureza = "C" if valor >= 0 else "D"

                movimentos.append({
                    "data": data_mov,
                    "valor": abs(valor),
                    "descricao": memo,
                    "documento": fitid,
                    "natureza": natureza,
                })
            except (ValueError, InvalidOperation):
                continue

        return movimentos

    def _parsear_csv(self, conteudo: str) -> list[dict]:
        """Parser CSV simples: data;valor;descricao (separador ; ou ,)."""
        movimentos = []
        for i, linha in enumerate(conteudo.splitlines()):
            if i == 0 and not linha[0].isdigit():
                continue  # pula cabeçalho
            sep = ";" if ";" in linha else ","
            partes = linha.strip().split(sep)
            if len(partes) < 2:
                continue
            try:
                data_str = partes[0].strip()
                valor_str = partes[1].strip().replace(".", "").replace(",", ".")
                descricao = partes[2].strip() if len(partes) > 2 else "Sem descrição"

                # Tenta múltiplos formatos de data
                for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
                    try:
                        data_mov = date(*[int(x) for x in __import__("re").split(r"[-/]", data_str)])
                        break
                    except Exception:
                        from datetime import datetime
                        try:
                            data_mov = datetime.strptime(data_str, fmt).date()
                            break
                        except ValueError:
                            continue

                valor = Decimal(valor_str)
                natureza = "C" if valor >= 0 else "D"

                movimentos.append({
                    "data": data_mov,
                    "valor": abs(valor),
                    "descricao": descricao,
                    "documento": "",
                    "natureza": natureza,
                })
            except Exception:
                continue

        return movimentos

    def _parsear_cnab(self, conteudo: str) -> list[dict]:
        """
        Parser CNAB 240 simplificado.
        Segmento T (linha tipo '3' com posição 13 = 'T') contém valor e data.
        Esta implementação cobre o layout básico Bradesco/Itaú/BB.
        """
        movimentos = []
        for linha in conteudo.splitlines():
            if len(linha) < 240:
                continue
            tipo_registro = linha[7]
            segmento = linha[13] if len(linha) > 13 else ""

            if tipo_registro == "3" and segmento == "T":
                try:
                    data_str = linha[143:151]  # DDMMAAAA
                    valor_str = linha[152:167].strip()
                    descricao = linha[53:93].strip()
                    nosso_num = linha[93:113].strip()

                    data_mov = date(int(data_str[4:8]), int(data_str[2:4]), int(data_str[:2]))
                    valor = Decimal(valor_str) / Decimal("100")  # centavos

                    movimentos.append({
                        "data": data_mov,
                        "valor": valor,
                        "descricao": descricao or "CNAB movimento",
                        "documento": nosso_num,
                        "natureza": "C",  # retorno = crédito geralmente
                    })
                except Exception:
                    continue

        return movimentos

    # ──────────────────────────────────────────────
    # Processamento de cada movimento
    # ──────────────────────────────────────────────

    def _processar_movimento(
        self, importacao, mov_raw: dict,
        status_conc, status_pend, status_div,
        dry_run: bool,
    ) -> str:
        """
        Para cada movimento:
        1. Cria MovimentoBancario
        2. Tenta match com LancamentoFinanceiro
        3. Se match: cria ConciliacaoBancaria + baixa CP/CR
        4. Se não: cria DivergenciaConciliacao
        """
        with transaction.atomic():
            # 1. Cria o movimento bancário
            if not dry_run:
                tipo_mov = TipoMovimentoBancario.objects.filter(
                    natureza=mov_raw["natureza"]
                ).first()
                movimento = MovimentoBancario.objects.create(
                    importacao=importacao,
                    conta_bancaria=importacao.conta_bancaria,
                    tipo_movimento=tipo_mov,
                    data_movimento=mov_raw["data"],
                    valor=mov_raw["valor"],
                    descricao=mov_raw["descricao"],
                    documento=mov_raw.get("documento", ""),
                    status_conciliacao=status_pend,
                )
            else:
                movimento = None

            # 2. Tenta match com lançamento interno
            lancamento_match = self._buscar_lancamento_match(importacao, mov_raw)

            if lancamento_match:
                # 3. Concilia
                if not dry_run:
                    diferenca = abs(lancamento_match.valor - mov_raw["valor"])
                    ConciliacaoBancaria.objects.create(
                        empresa=importacao.empresa,
                        movimento_bancario=movimento,
                        lancamento=lancamento_match,
                        status=status_conc,
                        automatica=True,
                        diferenca=diferenca,
                        observacao="Conciliação automática por valor + data.",
                    )
                    movimento.status_conciliacao = status_conc
                    movimento.save(update_fields=["status_conciliacao"])

                    lancamento_match.conciliado = True
                    lancamento_match.save(update_fields=["conciliado"])

                    # Baixa automática em CP/CR
                    self._dar_baixa(lancamento_match, mov_raw)

                self.stdout.write(f"    ✓ CONCILIADO: {mov_raw['data']} R${mov_raw['valor']:.2f}")
                return "conciliado"
            else:
                # 4. Registra divergência
                if not dry_run:
                    DivergenciaConciliacao.objects.create(
                        empresa=importacao.empresa,
                        movimento_bancario=movimento,
                        tipo_divergencia="SEM_LANCAMENTO",
                        valor_extrato=mov_raw["valor"],
                    )
                    movimento.status_conciliacao = status_div
                    movimento.save(update_fields=["status_conciliacao"])

                self.stdout.write(f"    ✗ SEM MATCH: {mov_raw['data']} R${mov_raw['valor']:.2f} — {mov_raw['descricao'][:40]}")
                return "divergente"

    def _buscar_lancamento_match(self, importacao, mov_raw: dict):
        """
        Busca LancamentoFinanceiro compatível por:
        - mesma empresa e conta bancária
        - valor dentro da tolerância
        - data dentro de ±TOLERANCIA_DIAS dias
        - ainda não conciliado
        """
        data_min = mov_raw["data"] - timedelta(days=TOLERANCIA_DIAS)
        data_max = mov_raw["data"] + timedelta(days=TOLERANCIA_DIAS)
        valor_min = mov_raw["valor"] - TOLERANCIA_VALOR
        valor_max = mov_raw["valor"] + TOLERANCIA_VALOR
        natureza = mov_raw["natureza"]

        return (
            LancamentoFinanceiro.objects
            .filter(
                empresa=importacao.empresa,
                conta_bancaria=importacao.conta_bancaria,
                conciliado=False,
                data_lancamento__gte=data_min,
                data_lancamento__lte=data_max,
                valor__gte=valor_min,
                valor__lte=valor_max,
                tipo_lancamento__natureza=natureza,
            )
            .order_by("data_lancamento")
            .first()
        )

    def _dar_baixa(self, lancamento: LancamentoFinanceiro, mov_raw: dict):
        """
        Se o lançamento está vinculado a uma CP ou CR, dá a baixa automática:
        - Define data_pagamento = data do movimento
        - Define valor_pago = valor do movimento
        - Muda status para o primeiro finalizado disponível
        """
        hoje = mov_raw["data"]

        if lancamento.conta_pagar_id:
            try:
                cp = ContaPagar.objects.select_related("status").get(pk=lancamento.conta_pagar_id)
                if not cp.status.finalizado:
                    status_pago = cp.status.__class__.objects.filter(
                        finalizado=True, ativo=True
                    ).order_by("pk").first()
                    if status_pago:
                        cp.status = status_pago
                        cp.data_pagamento = hoje
                        cp.valor_pago = mov_raw["valor"]
                        cp.save(update_fields=["status", "data_pagamento", "valor_pago"])
                        self.stdout.write(f"      → Baixa em CP #{cp.pk}: {cp.descricao[:40]}")
            except ContaPagar.DoesNotExist:
                pass

        if lancamento.conta_receber_id:
            try:
                cr = ContaReceber.objects.select_related("cliente", "status").get(pk=lancamento.conta_receber_id)
                if not cr.status.finalizado:
                    status_recebido = cr.status.__class__.objects.filter(
                        finalizado=True, ativo=True
                    ).order_by("pk").first()
                    if status_recebido:
                        cr.status = status_recebido
                        cr.data_pagamento = hoje
                        cr.valor_recebido = mov_raw["valor"]
                        cr.save(update_fields=["status", "data_pagamento", "valor_recebido"])

                        # Registra histórico de pagamento
                        from apps.financeiro.models import HistoricoPagamentoCliente
                        if cr.cliente_id:
                            dias_atraso = max(0, (hoje - cr.data_vencimento).days)
                            HistoricoPagamentoCliente.objects.create(
                                empresa=cr.empresa,
                                cliente=cr.cliente,
                                conta_receber=cr,
                                valor_pago=mov_raw["valor"],
                                data_pagamento=hoje,
                                dias_atraso=dias_atraso,
                            )
                        self.stdout.write(f"      → Baixa em CR #{cr.pk}: {cr.descricao[:40]}")
            except ContaReceber.DoesNotExist:
                pass