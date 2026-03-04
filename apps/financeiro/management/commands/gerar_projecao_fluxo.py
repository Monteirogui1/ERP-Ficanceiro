"""
Uso:
    python manage.py gerar_projecao_fluxo
    python manage.py gerar_projecao_fluxo --dias=60 --dry-run
    python manage.py gerar_projecao_fluxo --limpar  # apaga projeções automáticas antigas

manage.py gerar_projecao_fluxo --limpar >> projecao.log 2>&1
"""

from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.financeiro.models import (
    ContaPagar, ContaReceber,
    ProjecaoFluxoCaixa, TipoCenarioFluxo,
)
from apps.sistema.models import ContaBancaria


class Command(BaseCommand):
    help = "Gera projeção automática de fluxo de caixa por cenário."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dias", type=int, default=90,
            help="Quantos dias à frente projetar (padrão: 90).",
        )
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Simula sem gravar no banco.",
        )
        parser.add_argument(
            "--limpar", action="store_true",
            help="Remove projeções automáticas anteriores antes de gerar.",
        )
        parser.add_argument(
            "--agrupamento", choices=["diario", "semanal", "mensal"], default="mensal",
            help="Agrupamento das projeções (padrão: mensal).",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        dias = options["dias"]
        limpar = options["limpar"]
        agrupamento = options["agrupamento"]
        hoje = date.today()
        data_fim = hoje + timedelta(days=dias)

        self.stdout.write(
            self.style.NOTICE(
                f"[{timezone.now():%Y-%m-%d %H:%M}] Gerando projeção de fluxo "
                f"({agrupamento}, {dias} dias, dry_run={dry_run})"
            )
        )

        # Coleta todos os cenários ativos
        cenarios = list(TipoCenarioFluxo.objects.filter(ativo=True))
        if not cenarios:
            self.stdout.write(self.style.WARNING("Nenhum cenário de fluxo cadastrado."))
            return

        # Coleta todas as empresas com CP/CR em aberto
        empresas_ids = set(
            ContaPagar.objects.filter(
                status__finalizado=False, data_vencimento__gte=hoje
            ).values_list("empresa_id", flat=True)
        ) | set(
            ContaReceber.objects.filter(
                status__finalizado=False, data_vencimento__gte=hoje
            ).values_list("empresa_id", flat=True)
        )

        total_criadas = 0

        for empresa_id in empresas_ids:
            for cenario in cenarios:
                n = self._gerar_para_empresa_cenario(
                    empresa_id, cenario, hoje, data_fim,
                    agrupamento, dry_run, limpar,
                )
                total_criadas += n

        self.stdout.write(
            self.style.SUCCESS(f"Concluído: {total_criadas} projeção(ões) criada(s).")
        )

    # ──────────────────────────────────────────────
    # Core: gera projeções para empresa × cenário
    # ──────────────────────────────────────────────

    def _gerar_para_empresa_cenario(
        self, empresa_id: int, cenario: "TipoCenarioFluxo",
        hoje: date, data_fim: date,
        agrupamento: str, dry_run: bool, limpar: bool,
    ) -> int:
        # Remove projeções automáticas antigas deste cenário
        if limpar and not dry_run:
            ProjecaoFluxoCaixa.objects.filter(
                empresa_id=empresa_id,
                cenario=cenario,
                gerado_automaticamente=True,
                data_referencia__gte=hoje,
            ).delete()

        # Agrupa CP em aberto por período
        cp_abertas = (
            ContaPagar.objects
            .filter(
                empresa_id=empresa_id,
                status__finalizado=False,
                data_vencimento__gte=hoje,
                data_vencimento__lte=data_fim,
            )
            .values("data_vencimento", "conta_bancaria_id", "valor_original")
        )

        cr_abertas = (
            ContaReceber.objects
            .filter(
                empresa_id=empresa_id,
                status__finalizado=False,
                data_vencimento__gte=hoje,
                data_vencimento__lte=data_fim,
            )
            .values("data_vencimento", "conta_bancaria_id", "valor_original")
        )

        # Agrupa por período × conta bancária
        # chave: (data_referencia, conta_bancaria_id)
        saidas: dict = defaultdict(Decimal)
        entradas: dict = defaultdict(Decimal)

        for cp in cp_abertas:
            chave = (
                self._periodo_chave(cp["data_vencimento"], agrupamento),
                cp["conta_bancaria_id"],
            )
            saidas[chave] += Decimal(str(cp["valor_original"]))

        for cr in cr_abertas:
            chave = (
                self._periodo_chave(cr["data_vencimento"], agrupamento),
                cr["conta_bancaria_id"],
            )
            entradas[chave] += Decimal(str(cr["valor_original"]))

        # Une todas as chaves (períodos com CP ou CR)
        todas_chaves = set(saidas.keys()) | set(entradas.keys())

        fator = Decimal("1") + (cenario.percentual_ajuste / Decimal("100"))
        projecoes_a_criar = []

        for (data_ref, conta_id) in sorted(todas_chaves):
            entrada_base = entradas.get((data_ref, conta_id), Decimal("0"))
            saida_base = saidas.get((data_ref, conta_id), Decimal("0"))

            # Aplica fator do cenário
            entrada_ajustada = (entrada_base * fator).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            saida_ajustada = (saida_base * fator).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            saldo = entrada_ajustada - saida_ajustada

            projecoes_a_criar.append(
                ProjecaoFluxoCaixa(
                    empresa_id=empresa_id,
                    conta_bancaria_id=conta_id,
                    cenario=cenario,
                    data_referencia=data_ref,
                    entradas_previstas=entrada_ajustada,
                    saidas_previstas=saida_ajustada,
                    saldo_projetado=saldo,
                    gerado_automaticamente=True,
                )
            )

            self.stdout.write(
                f"  empresa={empresa_id} cenario={cenario.nome} "
                f"data={data_ref} conta={conta_id or 'geral'} | "
                f"ent={entrada_ajustada:.2f} sai={saida_ajustada:.2f} saldo={saldo:.2f}"
            )

        if not dry_run and projecoes_a_criar:
            with transaction.atomic():
                ProjecaoFluxoCaixa.objects.bulk_create(projecoes_a_criar)

        return len(projecoes_a_criar)

    # ──────────────────────────────────────────────
    # Agrupamento de datas
    # ──────────────────────────────────────────────

    @staticmethod
    def _periodo_chave(data: date, agrupamento: str) -> date:
        """
        Retorna a data representativa do período:
        - diário:  própria data
        - semanal: segunda-feira da semana
        - mensal:  1º dia do mês
        """
        if agrupamento == "diario":
            return data
        elif agrupamento == "semanal":
            return data - timedelta(days=data.weekday())  # segunda da semana
        else:  # mensal
            return data.replace(day=1)