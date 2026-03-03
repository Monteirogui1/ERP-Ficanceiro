from django.db import models
from apps.authentication.models import ModeloBase, Empresa, Usuario
from apps.sistema.models import PlanoContas


# ══════════════════════════════════════════════
# CHOICES CADASTRÁVEIS
# ══════════════════════════════════════════════

class TipoImposto(ModeloBase):
    """Ex: IRPJ, CSLL, PIS, COFINS, ISS, ICMS, IPI, INSS, FGTS, IRRF, SIMPLES"""
    nome = models.CharField(max_length=100, unique=True)
    sigla = models.CharField(max_length=20, unique=True)
    esfera = models.CharField(
        max_length=10,
        choices=[("FEDERAL", "Federal"), ("ESTADUAL", "Estadual"), ("MUNICIPAL", "Municipal")]
    )
    base_calculo_padrao = models.CharField(max_length=100, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Imposto"


class TipoObrigacaoFiscal(ModeloBase):
    """Ex: DCTF, EFD-ICMS/IPI, ECD, ECF, SPED Fiscal, DIRF, RAIS, CAGED"""
    nome = models.CharField(max_length=100, unique=True)
    sigla = models.CharField(max_length=20, blank=True)
    periodicidade = models.CharField(
        max_length=20,
        choices=[
            ("MENSAL", "Mensal"), ("TRIMESTRAL", "Trimestral"),
            ("SEMESTRAL", "Semestral"), ("ANUAL", "Anual"), ("EVENTUAL", "Eventual")
        ]
    )
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Obrigação Fiscal"


class StatusObrigacaoFiscal(ModeloBase):
    """Ex: Pendente, Em Preenchimento, Entregue, Retificado, Atrasado"""
    nome = models.CharField(max_length=50, unique=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Status de Obrigação Fiscal"


# ══════════════════════════════════════════════
# CONFIGURAÇÃO DE IMPOSTOS
# ══════════════════════════════════════════════

class ConfiguracaoImpostoEmpresa(ModeloBase):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="configuracoes_imposto")
    tipo_imposto = models.ForeignKey(TipoImposto, on_delete=models.PROTECT)
    aliquota = models.DecimalField(max_digits=8, decimal_places=4)
    plano_contas_debito = models.ForeignKey(
        PlanoContas, on_delete=models.SET_NULL, null=True, blank=True, related_name="impostos_debito"
    )
    plano_contas_credito = models.ForeignKey(
        PlanoContas, on_delete=models.SET_NULL, null=True, blank=True, related_name="impostos_credito"
    )
    vigencia_inicio = models.DateField()
    vigencia_fim = models.DateField(null=True, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Configuração de Imposto da Empresa"
        unique_together = ("empresa", "tipo_imposto", "vigencia_inicio")


class LancamentoImposto(ModeloBase):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="lancamentos_imposto")
    tipo_imposto = models.ForeignKey(TipoImposto, on_delete=models.PROTECT)
    configuracao = models.ForeignKey(ConfiguracaoImpostoEmpresa, on_delete=models.SET_NULL, null=True, blank=True)
    competencia = models.DateField()
    data_vencimento = models.DateField()
    base_calculo = models.DecimalField(max_digits=15, decimal_places=2)
    aliquota_aplicada = models.DecimalField(max_digits=8, decimal_places=4)
    valor_calculado = models.DecimalField(max_digits=15, decimal_places=2)
    valor_pago = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    data_pagamento = models.DateField(null=True, blank=True)
    numero_guia = models.CharField(max_length=50, blank=True)
    observacoes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Lançamento de Imposto"
        ordering = ["data_vencimento"]


class ObrigacaoFiscal(ModeloBase):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="obrigacoes_fiscais")
    tipo = models.ForeignKey(TipoObrigacaoFiscal, on_delete=models.PROTECT)
    status = models.ForeignKey(StatusObrigacaoFiscal, on_delete=models.PROTECT, null=True)
    competencia = models.DateField()
    data_vencimento = models.DateField()
    data_entrega = models.DateField(null=True, blank=True)
    numero_protocolo = models.CharField(max_length=100, blank=True)
    arquivo = models.FileField(upload_to="fiscal/obrigacoes/", null=True, blank=True)
    responsavel = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    observacoes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Obrigação Fiscal"
        ordering = ["data_vencimento"]