"""
manage.py gerar_recorrencias >> recorrencias.log 2>&1
"""

from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.financeiro.models import (
    ContaPagar, ContaReceber, PeriodicidadeRecorrencia
)


class Command(BaseCommand):
    help = "Gera próximas ocorrências de lançamentos financeiros recorrentes."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simula a execução sem gravar no banco.",
        )
        parser.add_argument(
            "--dias-antecedencia",
            type=int,
            default=0,
            help="Gera a próxima parcela N dias antes do vencimento atual (padrão: 0).",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        antecedencia = options["dias_antecedencia"]
        hoje = date.today()
        limite = hoje + timedelta(days=antecedencia)

        self.stdout.write(
            self.style.NOTICE(
                f"[{timezone.now():%Y-%m-%d %H:%M}] Iniciando geração de recorrências "
                f"(dry_run={dry_run}, antecedencia={antecedencia} dias)"
            )
        )

        total_cp = self._processar_contas_pagar(hoje, limite, dry_run)
        total_cr = self._processar_contas_receber(hoje, limite, dry_run)

        self.stdout.write(
            self.style.SUCCESS(
                f"Concluído: {total_cp} ContaPagar e {total_cr} ContaReceber geradas."
            )
        )

    # ──────────────────────────────────────────────
    # CONTAS A PAGAR
    # ──────────────────────────────────────────────

    def _processar_contas_pagar(self, hoje: date, limite: date, dry_run: bool) -> int:
        """
        Seleciona ContaPagar recorrentes cujo vencimento <= limite
        e que ainda não geraram a próxima ocorrência.
        """
        candidatas = (
            ContaPagar.objects
            .filter(
                recorrente=True,
                periodicidade__isnull=False,
                status__finalizado=True,       # já foi paga/finalizada
                data_vencimento__lte=limite,
            )
            .select_related("periodicidade", "status", "empresa")
            .exclude(
                # Evita duplicatas: já existe filha com data de vencimento futura
                geradas_por_recorrencia__data_vencimento__gt=hoje
            )
        )

        geradas = 0
        for cp in candidatas:
            if cp.data_fim_recorrencia and hoje > cp.data_fim_recorrencia:
                continue  # recorrência encerrada

            proxima_data = self._proxima_data(cp.data_vencimento, cp.periodicidade)
            if cp.data_fim_recorrencia and proxima_data > cp.data_fim_recorrencia:
                continue

            if not dry_run:
                self._criar_proxima_cp(cp, proxima_data)

            self.stdout.write(
                f"  [CP] {cp.descricao[:50]} → próximo vencimento: {proxima_data:%d/%m/%Y}"
            )
            geradas += 1

        return geradas

    def _criar_proxima_cp(self, origem: "ContaPagar", proxima_data: date) -> "ContaPagar":
        with transaction.atomic():
            nova = ContaPagar(
                empresa=origem.empresa,
                fornecedor=origem.fornecedor,
                tipo_documento=origem.tipo_documento,
                descricao=origem.descricao,
                plano_contas=origem.plano_contas,
                centro_custo=origem.centro_custo,
                conta_bancaria=origem.conta_bancaria,
                forma_pagamento=origem.forma_pagamento,
                status=origem.status.__class__.objects.filter(
                    finalizado=False, ativo=True
                ).order_by("pk").first(),   # status "Pendente" ou equivalente
                valor_original=origem.valor_original,
                data_emissao=date.today(),
                data_vencimento=proxima_data,
                data_competencia=proxima_data,
                numero_parcelas=origem.numero_parcelas,
                numero_parcela_atual=origem.numero_parcela_atual + 1,
                recorrente=True,
                periodicidade=origem.periodicidade,
                data_fim_recorrencia=origem.data_fim_recorrencia,
                conta_pagar_origem=origem,
                requer_aprovacao=origem.requer_aprovacao,
                observacoes=f"[Gerado automaticamente em {date.today():%d/%m/%Y}] {origem.observacoes}",
            )
            nova.save()
        return nova

    # ──────────────────────────────────────────────
    # CONTAS A RECEBER
    # ──────────────────────────────────────────────

    def _processar_contas_receber(self, hoje: date, limite: date, dry_run: bool) -> int:
        candidatas = (
            ContaReceber.objects
            .filter(
                recorrente=True,
                periodicidade__isnull=False,
                status__finalizado=True,
                data_vencimento__lte=limite,
            )
            .select_related("periodicidade", "status", "empresa")
            .exclude(
                geradas_por_recorrencia__data_vencimento__gt=hoje
            )
        )

        geradas = 0
        for cr in candidatas:
            if cr.data_fim_recorrencia and hoje > cr.data_fim_recorrencia:
                continue

            proxima_data = self._proxima_data(cr.data_vencimento, cr.periodicidade)
            if cr.data_fim_recorrencia and proxima_data > cr.data_fim_recorrencia:
                continue

            if not dry_run:
                self._criar_proxima_cr(cr, proxima_data)

            self.stdout.write(
                f"  [CR] {cr.descricao[:50]} → próximo vencimento: {proxima_data:%d/%m/%Y}"
            )
            geradas += 1

        return geradas

    def _criar_proxima_cr(self, origem: "ContaReceber", proxima_data: date) -> "ContaReceber":
        with transaction.atomic():
            status_aberto = origem.status.__class__.objects.filter(
                finalizado=False, ativo=True
            ).order_by("pk").first()

            nova = ContaReceber(
                empresa=origem.empresa,
                cliente=origem.cliente,
                tipo_documento=origem.tipo_documento,
                descricao=origem.descricao,
                plano_contas=origem.plano_contas,
                centro_custo=origem.centro_custo,
                conta_bancaria=origem.conta_bancaria,
                forma_pagamento=origem.forma_pagamento,
                status=status_aberto,
                valor_original=origem.valor_original,
                data_emissao=date.today(),
                data_vencimento=proxima_data,
                data_competencia=proxima_data,
                numero_parcelas=origem.numero_parcelas,
                numero_parcela_atual=origem.numero_parcela_atual + 1,
                recorrente=True,
                periodicidade=origem.periodicidade,
                data_fim_recorrencia=origem.data_fim_recorrencia,
                conta_receber_origem=origem,
                em_cobranca=False,
                observacoes=f"[Gerado automaticamente em {date.today():%d/%m/%Y}] {origem.observacoes}",
            )
            nova.save()
        return nova

    # ──────────────────────────────────────────────
    # Utilitário de data
    # ──────────────────────────────────────────────

    @staticmethod
    def _proxima_data(data_base: date, periodicidade: "PeriodicidadeRecorrencia") -> date:
        """
        Calcula a próxima data com base nos dias_intervalo da periodicidade.
        Fallback para 30 dias se dias_intervalo não estiver definido.
        """
        intervalo = periodicidade.dias_intervalo or 30
        return data_base + timedelta(days=intervalo)