from datetime import timedelta
from decimal import Decimal

from django.db import transaction

from apps.bancario.models import (
    MovimentoBancario, ConciliacaoBancaria,
    DivergenciaConciliacao, StatusConciliacao,
)
from apps.financeiro.models import LancamentoFinanceiro


TOLERANCIA_VALOR = Decimal("0.10")
SCORE_MINIMO = 60


class ConciliacaoAutomaticaService:
    """
    Serviço reutilizável de conciliação automática.

    Uso:
        from apps.bancario.services.conciliacao_automatica import ConciliacaoAutomaticaService
        resultado = ConciliacaoAutomaticaService(importacao, usuario=request.user).executar()
        print(resultado)  # {"conciliados": 12, "divergentes": 3, "ignorados": 1}
    """

    def __init__(self, importacao, usuario=None, dry_run: bool = False):
        self.importacao = importacao
        self.empresa = importacao.empresa
        self.conta = importacao.conta_bancaria
        self.usuario = usuario
        self.dry_run = dry_run

        self._status_conciliado, _ = StatusConciliacao.objects.get_or_create(nome="Conciliada")
        self._status_pendente, _ = StatusConciliacao.objects.get_or_create(nome="Pendente")
        self._status_divergente, _ = StatusConciliacao.objects.get_or_create(nome="Divergente")

    def executar(self) -> dict:
        movimentos = (
            MovimentoBancario.objects
            .filter(
                importacao=self.importacao,
                status_conciliacao=self._status_pendente,
            )
            .select_related("tipo_movimento")
            .order_by("data_movimento")
        )

        # Pré-carrega lançamentos não conciliados da conta
        lancamentos_disponiveis = list(
            LancamentoFinanceiro.objects
            .filter(
                empresa=self.empresa,
                conta_bancaria=self.conta,
                conciliado=False,
            )
            .select_related("tipo_lancamento")
        )

        resultado = {"conciliados": 0, "divergentes": 0, "ignorados": 0}
        lancamentos_usados = set()

        for movimento in movimentos:
            candidatos = self._filtrar_candidatos(movimento, lancamentos_disponiveis, lancamentos_usados)
            melhor = self._selecionar_melhor(movimento, candidatos)

            if melhor and melhor["score"] >= SCORE_MINIMO:
                lancamento = melhor["lancamento"]
                if not self.dry_run:
                    self._conciliar(movimento, lancamento, melhor["score"])
                lancamentos_usados.add(lancamento.pk)
                resultado["conciliados"] += 1
            else:
                if not self.dry_run:
                    self._registrar_divergencia(movimento)
                resultado["divergentes"] += 1

        # Lançamentos sem movimento bancário correspondente
        lancamentos_sem_movimento = [
            l for l in lancamentos_disponiveis
            if l.pk not in lancamentos_usados
            and self._data_no_periodo(l.data_lancamento)
        ]
        for lanc in lancamentos_sem_movimento:
            if not self.dry_run:
                DivergenciaConciliacao.objects.get_or_create(
                    empresa=self.empresa,
                    lancamento=lanc,
                    tipo_divergencia="SEM_MOVIMENTO",
                    defaults={"valor_sistema": lanc.valor},
                )
            resultado["ignorados"] += 1

        return resultado

    # ──────────────────────────────────────────────
    # Filtragem de candidatos
    # ──────────────────────────────────────────────

    def _filtrar_candidatos(
        self, movimento: MovimentoBancario,
        lancamentos: list, usados: set,
    ) -> list:
        """
        Pré-filtra lançamentos por natureza e janela de data ±3 dias
        para reduzir o espaço de busca antes de calcular o score.
        """
        natureza_mov = movimento.tipo_movimento.natureza if movimento.tipo_movimento else None
        data_min = movimento.data_movimento - timedelta(days=3)
        data_max = movimento.data_movimento + timedelta(days=3)
        valor_min = abs(movimento.valor) - TOLERANCIA_VALOR
        valor_max = abs(movimento.valor) + TOLERANCIA_VALOR

        return [
            l for l in lancamentos
            if l.pk not in usados
            and data_min <= l.data_lancamento <= data_max
            and valor_min <= abs(l.valor) <= valor_max
            and (natureza_mov is None or l.tipo_lancamento.natureza == natureza_mov)
        ]

    # ──────────────────────────────────────────────
    # Score de similaridade
    # ──────────────────────────────────────────────

    def _selecionar_melhor(self, movimento: MovimentoBancario, candidatos: list) -> dict | None:
        if not candidatos:
            return None

        melhor = None
        for lanc in candidatos:
            score = self._calcular_score(movimento, lanc)
            if melhor is None or score > melhor["score"]:
                melhor = {"lancamento": lanc, "score": score}

        return melhor

    def _calcular_score(self, movimento: MovimentoBancario, lancamento: LancamentoFinanceiro) -> int:
        score = 0
        diff_valor = abs(abs(movimento.valor) - abs(lancamento.valor))

        # Valor
        if diff_valor == Decimal("0"):
            score += 40
        elif diff_valor <= TOLERANCIA_VALOR:
            score += 25

        # Data
        diff_dias = abs((movimento.data_movimento - lancamento.data_lancamento).days)
        if diff_dias == 0:
            score += 30
        elif diff_dias == 1:
            score += 20
        elif diff_dias <= 3:
            score += 10

        # Documento / nosso número
        doc_mov = (movimento.documento or "").strip().lstrip("0")
        doc_lanc = (lancamento.numero_documento or "").strip().lstrip("0")
        if doc_mov and doc_lanc and doc_mov == doc_lanc:
            score += 20

        # Similaridade textual na descrição (básica)
        desc_mov = movimento.descricao.lower()
        desc_lanc = lancamento.descricao.lower()
        palavras_lanc = set(w for w in desc_lanc.split() if len(w) > 3)
        if palavras_lanc:
            palavras_em_comum = sum(1 for p in palavras_lanc if p in desc_mov)
            if palavras_em_comum >= 2:
                score += 10
            elif palavras_em_comum == 1:
                score += 5

        return score

    # ──────────────────────────────────────────────
    # Persistência
    # ──────────────────────────────────────────────

    def _conciliar(
        self,
        movimento: MovimentoBancario,
        lancamento: LancamentoFinanceiro,
        score: int,
    ):
        diferenca = abs(abs(movimento.valor) - abs(lancamento.valor))
        with transaction.atomic():
            ConciliacaoBancaria.objects.create(
                empresa=self.empresa,
                movimento_bancario=movimento,
                lancamento=lancamento,
                status=self._status_conciliado,
                automatica=True,
                diferenca=diferenca,
                conciliado_por=self.usuario,
                observacao=f"Conciliação automática (score={score}/100). "
                           f"Diferença: R$ {diferenca:.2f}",
            )

            movimento.status_conciliacao = self._status_conciliado
            movimento.save(update_fields=["status_conciliacao"])

            lancamento.conciliado = True
            lancamento.save(update_fields=["conciliado"])

            # Resolve divergência anterior se existia
            DivergenciaConciliacao.objects.filter(
                lancamento=lancamento, resolvida=False
            ).update(resolvida=True, resolucao="Conciliado automaticamente.")
            DivergenciaConciliacao.objects.filter(
                movimento_bancario=movimento, resolvida=False
            ).update(resolvida=True, resolucao="Conciliado automaticamente.")

    def _registrar_divergencia(self, movimento: MovimentoBancario):
        with transaction.atomic():
            DivergenciaConciliacao.objects.get_or_create(
                empresa=self.empresa,
                movimento_bancario=movimento,
                tipo_divergencia="SEM_LANCAMENTO",
                defaults={"valor_extrato": abs(movimento.valor)},
            )
            movimento.status_conciliacao = self._status_divergente
            movimento.save(update_fields=["status_conciliacao"])

    # ──────────────────────────────────────────────
    # Utilitário
    # ──────────────────────────────────────────────

    def _data_no_periodo(self, data: "date") -> bool:
        if not self.importacao.data_inicio_extrato or not self.importacao.data_fim_extrato:
            return True
        return self.importacao.data_inicio_extrato <= data <= self.importacao.data_fim_extrato



"""
Para usar como management command, crie:
apps/bancario/management/commands/conciliar_automatico.py

from django.core.management.base import BaseCommand, CommandError
from apps.bancario.models import ImportacaoExtrato
from apps.bancario.services.conciliacao_automatica import ConciliacaoAutomaticaService

class Command(BaseCommand):
    help = "Executa conciliação automática em uma importação de extrato."

    def add_arguments(self, parser):
        parser.add_argument("--importacao-id", type=int, required=True)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        try:
            importacao = ImportacaoExtrato.objects.get(pk=options["importacao_id"])
        except ImportacaoExtrato.DoesNotExist:
            raise CommandError(f"Importação #{options['importacao_id']} não encontrada.")

        svc = ConciliacaoAutomaticaService(importacao, dry_run=options["dry_run"])
        resultado = svc.executar()
        self.stdout.write(self.style.SUCCESS(str(resultado)))


Para chamar via view (ex: botão "Conciliar Automaticamente"):
from apps.bancario.services.conciliacao_automatica import ConciliacaoAutomaticaService

class ConciliarAutomaticoView(PermissaoModuloMixin, View):
    modulo = "bancario"
    acao = "editar"

    def post(self, request, pk):
        importacao = get_object_or_404(ImportacaoExtrato, pk=pk, empresa=self.get_empresa())
        svc = ConciliacaoAutomaticaService(importacao, usuario=request.user)
        resultado = svc.executar()
        messages.success(
            request,
            f"Conciliação concluída: {resultado['conciliados']} conciliados, "
            f"{resultado['divergentes']} divergentes."
        )
        return redirect("bancario:importacao_detail", pk=pk)
"""