from django.db import models
from apps.authentication.models import ModeloBase, Empresa, Usuario
from apps.sistema.models import PlanoContas, CentroCusto


# ══════════════════════════════════════════════
# CHOICES CADASTRÁVEIS
# ══════════════════════════════════════════════

class StatusOrcamento(ModeloBase):
    """Ex: Em Elaboração, Aprovado, Revisado, Encerrado"""
    nome = models.CharField(max_length=50, unique=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Status de Orçamento"


# ══════════════════════════════════════════════
# ORÇAMENTO
# ══════════════════════════════════════════════

class Orcamento(ModeloBase):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="orcamentos")
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    ano = models.PositiveSmallIntegerField()
    status = models.ForeignKey(StatusOrcamento, on_delete=models.PROTECT, null=True)
    aprovado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name="orcamentos_aprovados"
    )
    data_aprovacao = models.DateField(null=True, blank=True)
    criado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, related_name="orcamentos_criados"
    )

    class Meta:
        verbose_name = "Orçamento"
        unique_together = ("empresa", "ano", "nome")


class ItemOrcamento(ModeloBase):
    """Item orçamentário mensal — previsto vs realizado por conta e centro de custo."""
    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE, related_name="itens")
    plano_contas = models.ForeignKey(PlanoContas, on_delete=models.PROTECT)
    centro_custo = models.ForeignKey(CentroCusto, on_delete=models.SET_NULL, null=True, blank=True)
    mes = models.PositiveSmallIntegerField(help_text="1 = Janeiro … 12 = Dezembro")
    valor_previsto = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    valor_realizado = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    valor_revisado = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    percentual_execucao = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    alerta_estouro_enviado = models.BooleanField(default=False)
    observacoes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Item de Orçamento"
        unique_together = ("orcamento", "plano_contas", "centro_custo", "mes")


class AlertaEstouroOrcamento(ModeloBase):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="alertas_estouro")
    item_orcamento = models.ForeignKey(ItemOrcamento, on_delete=models.CASCADE, related_name="alertas")
    percentual_execucao_no_alerta = models.DecimalField(max_digits=7, decimal_places=2)
    valor_previsto = models.DecimalField(max_digits=15, decimal_places=2)
    valor_realizado = models.DecimalField(max_digits=15, decimal_places=2)
    notificacao_enviada = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Alerta de Estouro de Orçamento"
        ordering = ["-criado_em"]