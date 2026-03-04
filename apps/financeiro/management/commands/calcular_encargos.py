"""
Uso:
    python manage.py calcular_encargos
    python manage.py calcular_encargos --juros-dia=0.033 --multa=2.0 --dry-run

manage.py calcular_encargos >> encargos.log 2>&1
"""

from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.financeiro.models import (
    ContaReceber, ContaPagar,
    EncargoContaReceber, EncargoContaPagar,
    TipoEncargo,
)


# ── Defaults de encargo (% ao mês padrão Código Civil Brasileiro) ──
JUROS_PADRAO_DIA = Decimal("0.033333")   # 1% ao mês = 0,0333% ao dia
MULTA_PADRAO = Decimal("2.0")            # 2% de multa por inadimplência


class Command(BaseCommand):
    help = "Calcula e aplica juros e multa em lançamentos financeiros vencidos."

    def add_arguments(self, parser):
        parser.add_argument(
            "--juros-dia", type=float, default=float(JUROS_PADRAO_DIA),
            help="Percentual de juros ao dia (padrão: 0.0333 = 1%% a.m.).",
        )
        parser.add_argument(
            "--multa", type=float, default=float(MULTA_PADRAO),
            help="Percentual de multa aplicado no 1º dia de atraso (padrão: 2%%).",
        )
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Simula sem gravar no banco.",
        )
        parser.add_argument(
            "--apenas-cr", action="store_true",
            help="Aplica apenas em Contas a Receber.",
        )
        parser.add_argument(
            "--apenas-cp", action="store_true",
            help="Aplica apenas em Contas a Pagar.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        juros_dia = Decimal(str(options["juros_dia"]))
        multa_pct = Decimal(str(options["multa"]))
        apenas_cr = options["apenas_cr"]
        apenas_cp = options["apenas_cp"]
        hoje = date.today()

        self.stdout.write(
            self.style.NOTICE(
                f"[{timezone.now():%Y-%m-%d %H:%M}] Calculando encargos "
                f"(juros_dia={juros_dia}%, multa={multa_pct}%, dry_run={dry_run})"
            )
        )

        # Garante que os TipoEncargo existem
        tipo_juros = self._get_ou_criar_tipo_encargo("Juros de Mora", "A")
        tipo_multa = self._get_ou_criar_tipo_encargo("Multa por Inadimplência", "A")

        total_cr = total_cp = 0

        if not apenas_cp:
            total_cr = self._processar_contas_receber(
                hoje, juros_dia, multa_pct, tipo_juros, tipo_multa, dry_run
            )

        if not apenas_cr:
            total_cp = self._processar_contas_pagar(
                hoje, juros_dia, multa_pct, tipo_juros, tipo_multa, dry_run
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Concluído: {total_cr} encargos em CR | {total_cp} encargos em CP."
            )
        )

    # ──────────────────────────────────────────────
    # CONTAS A RECEBER
    # ──────────────────────────────────────────────

    def _processar_contas_receber(
        self, hoje, juros_dia, multa_pct, tipo_juros, tipo_multa, dry_run
    ) -> int:
        """
        Para cada CR vencida e não finalizada:
         1. Aplica multa (se ainda não foi aplicada)
         2. Aplica juros do dia (se não foi aplicado hoje)
        """
        vencidas = (
            ContaReceber.objects
            .filter(
                status__finalizado=False,
                data_vencimento__lt=hoje,
            )
            .select_related("empresa", "status")
            .prefetch_related("encargos__tipo_encargo")
        )

        total = 0
        for cr in vencidas:
            dias_atraso = (hoje - cr.data_vencimento).days
            encargos_existentes = cr.encargos.all()

            # ── Multa (somente no 1º dia de atraso) ──
            ja_tem_multa = encargos_existentes.filter(
                tipo_encargo=tipo_multa
            ).exists()

            if dias_atraso >= 1 and not ja_tem_multa:
                valor_multa = self._calcular_percentual(cr.valor_original, multa_pct)
                if not dry_run:
                    with transaction.atomic():
                        EncargoContaReceber.objects.create(
                            conta_receber=cr,
                            tipo_encargo=tipo_multa,
                            percentual=multa_pct,
                            valor=valor_multa,
                            data_aplicacao=cr.data_vencimento + __import__("datetime").timedelta(days=1),
                            observacao=f"Multa automática — {multa_pct}% sobre R$ {cr.valor_original:,.2f}",
                        )
                self.stdout.write(
                    f"  [CR-MULTA] #{cr.pk} {cr.descricao[:40]} | "
                    f"multa R$ {valor_multa:.2f}"
                )
                total += 1

            # ── Juros diários (um por dia, não repete no mesmo dia) ──
            ja_tem_juros_hoje = encargos_existentes.filter(
                tipo_encargo=tipo_juros,
                data_aplicacao=hoje,
            ).exists()

            if dias_atraso >= 1 and not ja_tem_juros_hoje:
                valor_juros = self._calcular_percentual(cr.valor_original, juros_dia)
                if not dry_run:
                    with transaction.atomic():
                        EncargoContaReceber.objects.create(
                            conta_receber=cr,
                            tipo_encargo=tipo_juros,
                            percentual=juros_dia,
                            valor=valor_juros,
                            data_aplicacao=hoje,
                            observacao=f"Juros automáticos dia {hoje:%d/%m/%Y} — "
                                       f"{juros_dia}%/dia × R$ {cr.valor_original:,.2f} "
                                       f"({dias_atraso} dia(s) de atraso)",
                        )
                self.stdout.write(
                    f"  [CR-JUROS] #{cr.pk} {cr.descricao[:40]} | "
                    f"juros R$ {valor_juros:.2f} (dia {dias_atraso})"
                )
                total += 1

        return total

    # ──────────────────────────────────────────────
    # CONTAS A PAGAR
    # ──────────────────────────────────────────────

    def _processar_contas_pagar(
        self, hoje, juros_dia, multa_pct, tipo_juros, tipo_multa, dry_run
    ) -> int:
        """
        Mesma lógica para CP — útil para controle de encargos
        de fornecedores que cobram juros por atraso.
        """
        vencidas = (
            ContaPagar.objects
            .filter(
                status__finalizado=False,
                data_vencimento__lt=hoje,
            )
            .select_related("empresa", "status")
            .prefetch_related("encargos__tipo_encargo")
        )

        total = 0
        for cp in vencidas:
            dias_atraso = (hoje - cp.data_vencimento).days
            encargos_existentes = cp.encargos.all()

            # Multa
            ja_tem_multa = encargos_existentes.filter(tipo_encargo=tipo_multa).exists()
            if dias_atraso >= 1 and not ja_tem_multa:
                valor_multa = self._calcular_percentual(cp.valor_original, multa_pct)
                if not dry_run:
                    with transaction.atomic():
                        EncargoContaPagar.objects.create(
                            conta_pagar=cp,
                            tipo_encargo=tipo_multa,
                            percentual=multa_pct,
                            valor=valor_multa,
                            data_aplicacao=cp.data_vencimento + __import__("datetime").timedelta(days=1),
                            observacao=f"Multa automática — {multa_pct}% sobre R$ {cp.valor_original:,.2f}",
                        )
                self.stdout.write(
                    f"  [CP-MULTA] #{cp.pk} {cp.descricao[:40]} | "
                    f"multa R$ {valor_multa:.2f}"
                )
                total += 1

            # Juros diários
            ja_tem_juros_hoje = encargos_existentes.filter(
                tipo_encargo=tipo_juros,
                data_aplicacao=hoje,
            ).exists()

            if dias_atraso >= 1 and not ja_tem_juros_hoje:
                valor_juros = self._calcular_percentual(cp.valor_original, juros_dia)
                if not dry_run:
                    with transaction.atomic():
                        EncargoContaPagar.objects.create(
                            conta_pagar=cp,
                            tipo_encargo=tipo_juros,
                            percentual=juros_dia,
                            valor=valor_juros,
                            data_aplicacao=hoje,
                            observacao=f"Juros automáticos dia {hoje:%d/%m/%Y} — "
                                       f"{juros_dia}%/dia × R$ {cp.valor_original:,.2f} "
                                       f"({dias_atraso} dia(s) de atraso)",
                        )
                self.stdout.write(
                    f"  [CP-JUROS] #{cp.pk} {cp.descricao[:40]} | "
                    f"juros R$ {valor_juros:.2f} (dia {dias_atraso})"
                )
                total += 1

        return total

    # ──────────────────────────────────────────────
    # Utilitários
    # ──────────────────────────────────────────────

    @staticmethod
    def _calcular_percentual(valor_base: Decimal, percentual: Decimal) -> Decimal:
        resultado = valor_base * (percentual / Decimal("100"))
        return resultado.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def _get_ou_criar_tipo_encargo(nome: str, natureza: str) -> "TipoEncargo":
        obj, _ = TipoEncargo.objects.get_or_create(
            nome=nome,
            defaults={"natureza": natureza},
        )
        return obj