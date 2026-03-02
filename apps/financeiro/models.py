from django.db import models
from apps.authentication.models import ModeloBase, Empresa, Usuario
from apps.sistema.models import Fornecedor, Cliente, ContaBancaria, PlanoContas, CentroCusto


# ══════════════════════════════════════════════
# CHOICES CADASTRÁVEIS
# ══════════════════════════════════════════════

class TipoDocumentoFinanceiro(ModeloBase):
    """Ex: Boleto, NF-e, Contrato, NFS-e, Fatura, Duplicata, Cheque"""
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="tipos_doc_financeiro")
    nome = models.CharField(max_length=100)
    requer_numero_documento = models.BooleanField(default=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Documento Financeiro"
        unique_together = ("empresa", "nome")


class TipoLancamento(ModeloBase):
    """Ex: Pagamento, Recebimento, Transferência, Estorno, Ajuste"""
    nome = models.CharField(max_length=100, unique=True)
    natureza = models.CharField(
        max_length=1,
        choices=[("D", "Débito"), ("C", "Crédito")]
    )
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Lançamento"


class FormaPagamento(ModeloBase):
    """Ex: Boleto, PIX, TED, DOC, Cheque, Cartão, Dinheiro, Débito Automático"""
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="formas_pagamento")
    nome = models.CharField(max_length=100)
    gera_arquivo_remessa = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Forma de Pagamento"
        unique_together = ("empresa", "nome")


class StatusContaPagar(ModeloBase):
    """Ex: Pendente, Aprovada, Paga, Cancelada, Vencida, Em Negociação"""
    nome = models.CharField(max_length=50, unique=True)
    finalizado = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Status de Conta a Pagar"


class StatusContaReceber(ModeloBase):
    """Ex: Aberta, Parcialmente Paga, Paga, Cancelada, Inadimplente, Protestada"""
    nome = models.CharField(max_length=50, unique=True)
    finalizado = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Status de Conta a Receber"


class PeriodicidadeRecorrencia(ModeloBase):
    """Ex: Diária, Semanal, Quinzenal, Mensal, Bimestral, Trimestral, Anual"""
    nome = models.CharField(max_length=50, unique=True)
    dias_intervalo = models.PositiveSmallIntegerField(null=True, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Periodicidade de Recorrência"


class TipoEncargo(ModeloBase):
    """Ex: Juros, Multa, Desconto, Correção Monetária, Taxas Bancárias"""
    nome = models.CharField(max_length=100, unique=True)
    natureza = models.CharField(
        max_length=1,
        choices=[("A", "Acréscimo"), ("D", "Desconto")]
    )
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Encargo"


class TipoCenarioFluxo(ModeloBase):
    """Ex: Otimista, Realista, Pessimista"""
    nome = models.CharField(max_length=50, unique=True)
    percentual_ajuste = models.DecimalField(
        max_digits=6, decimal_places=2, default=0,
        help_text="Ajuste % sobre o realista. Ex: +10 para otimista, -10 para pessimista."
    )
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Cenário de Fluxo de Caixa"


# ══════════════════════════════════════════════
# CONTAS A PAGAR
# ══════════════════════════════════════════════

class ContaPagar(ModeloBase):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="contas_pagar")
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.PROTECT, null=True, blank=True)
    tipo_documento = models.ForeignKey(TipoDocumentoFinanceiro, on_delete=models.PROTECT, null=True, blank=True)
    numero_documento = models.CharField(max_length=100, blank=True)
    descricao = models.CharField(max_length=300)
    plano_contas = models.ForeignKey(PlanoContas, on_delete=models.PROTECT, null=True, blank=True)
    centro_custo = models.ForeignKey(CentroCusto, on_delete=models.SET_NULL, null=True, blank=True)
    conta_bancaria = models.ForeignKey(ContaBancaria, on_delete=models.SET_NULL, null=True, blank=True)
    forma_pagamento = models.ForeignKey(FormaPagamento, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.ForeignKey(StatusContaPagar, on_delete=models.PROTECT, null=True)
    valor_original = models.DecimalField(max_digits=15, decimal_places=2)
    valor_pago = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    data_emissao = models.DateField()
    data_vencimento = models.DateField()
    data_pagamento = models.DateField(null=True, blank=True)
    data_competencia = models.DateField(null=True, blank=True)
    numero_parcelas = models.PositiveSmallIntegerField(default=1)
    numero_parcela_atual = models.PositiveSmallIntegerField(default=1)
    conta_pagar_pai = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="parcelas"
    )
    recorrente = models.BooleanField(default=False)
    periodicidade = models.ForeignKey(PeriodicidadeRecorrencia, on_delete=models.SET_NULL, null=True, blank=True)
    data_fim_recorrencia = models.DateField(null=True, blank=True)
    conta_pagar_origem = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="geradas_por_recorrencia"
    )
    requer_aprovacao = models.BooleanField(default=False)
    aprovado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name="aprovacoes_pagar"
    )
    data_aprovacao = models.DateTimeField(null=True, blank=True)
    observacoes = models.TextField(blank=True)
    criado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, related_name="contas_pagar_criadas"
    )

    class Meta:
        verbose_name = "Conta a Pagar"
        verbose_name_plural = "Contas a Pagar"
        ordering = ["data_vencimento"]


class EncargoContaPagar(ModeloBase):
    conta_pagar = models.ForeignKey(ContaPagar, on_delete=models.CASCADE, related_name="encargos")
    tipo_encargo = models.ForeignKey(TipoEncargo, on_delete=models.PROTECT)
    percentual = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    valor = models.DecimalField(max_digits=15, decimal_places=2)
    data_aplicacao = models.DateField()
    observacao = models.TextField(blank=True)

    class Meta:
        verbose_name = "Encargo de Conta a Pagar"


class DocumentoContaPagar(ModeloBase):
    conta_pagar = models.ForeignKey(ContaPagar, on_delete=models.CASCADE, related_name="documentos")
    nome = models.CharField(max_length=200)
    arquivo = models.FileField(upload_to="financeiro/contas_pagar/")
    tipo_arquivo = models.CharField(max_length=10, blank=True)
    tamanho_bytes = models.PositiveBigIntegerField(default=0)
    enviado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Documento de Conta a Pagar"


class AprovacaoContaPagar(ModeloBase):
    """Histórico de aprovações/rejeições na cadeia multinível."""
    conta_pagar = models.ForeignKey(ContaPagar, on_delete=models.CASCADE, related_name="historico_aprovacoes")
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    nivel_aprovacao = models.PositiveSmallIntegerField()
    decisao = models.CharField(
        max_length=10,
        choices=[("APROVADO", "Aprovado"), ("REJEITADO", "Rejeitado"), ("PENDENTE", "Pendente")]
    )
    justificativa = models.TextField(blank=True)

    class Meta:
        verbose_name = "Aprovação de Conta a Pagar"
        ordering = ["nivel_aprovacao", "criado_em"]


# ══════════════════════════════════════════════
# CONTAS A RECEBER
# ══════════════════════════════════════════════

class ContaReceber(ModeloBase):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="contas_receber")
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, null=True, blank=True)
    tipo_documento = models.ForeignKey(TipoDocumentoFinanceiro, on_delete=models.PROTECT, null=True, blank=True)
    numero_documento = models.CharField(max_length=100, blank=True)
    descricao = models.CharField(max_length=300)
    plano_contas = models.ForeignKey(PlanoContas, on_delete=models.PROTECT, null=True, blank=True)
    centro_custo = models.ForeignKey(CentroCusto, on_delete=models.SET_NULL, null=True, blank=True)
    conta_bancaria = models.ForeignKey(ContaBancaria, on_delete=models.SET_NULL, null=True, blank=True)
    forma_pagamento = models.ForeignKey(FormaPagamento, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.ForeignKey(StatusContaReceber, on_delete=models.PROTECT, null=True)
    valor_original = models.DecimalField(max_digits=15, decimal_places=2)
    valor_recebido = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    data_emissao = models.DateField()
    data_vencimento = models.DateField()
    data_recebimento = models.DateField(null=True, blank=True)
    data_competencia = models.DateField(null=True, blank=True)
    numero_parcelas = models.PositiveSmallIntegerField(default=1)
    numero_parcela_atual = models.PositiveSmallIntegerField(default=1)
    conta_receber_pai = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="parcelas"
    )
    recorrente = models.BooleanField(default=False)
    periodicidade = models.ForeignKey(PeriodicidadeRecorrencia, on_delete=models.SET_NULL, null=True, blank=True)
    data_fim_recorrencia = models.DateField(null=True, blank=True)
    conta_receber_origem = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="geradas_por_recorrencia"
    )
    nosso_numero = models.CharField(max_length=50, blank=True)
    linha_digitavel = models.CharField(max_length=200, blank=True)
    codigo_barras = models.CharField(max_length=200, blank=True)
    em_cobranca = models.BooleanField(default=False)
    data_protesto = models.DateField(null=True, blank=True)
    observacoes = models.TextField(blank=True)
    criado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, related_name="contas_receber_criadas"
    )

    class Meta:
        verbose_name = "Conta a Receber"
        verbose_name_plural = "Contas a Receber"
        ordering = ["data_vencimento"]


class EncargoContaReceber(ModeloBase):
    conta_receber = models.ForeignKey(ContaReceber, on_delete=models.CASCADE, related_name="encargos")
    tipo_encargo = models.ForeignKey(TipoEncargo, on_delete=models.PROTECT)
    percentual = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    valor = models.DecimalField(max_digits=15, decimal_places=2)
    data_aplicacao = models.DateField()
    observacao = models.TextField(blank=True)

    class Meta:
        verbose_name = "Encargo de Conta a Receber"


class DocumentoContaReceber(ModeloBase):
    conta_receber = models.ForeignKey(ContaReceber, on_delete=models.CASCADE, related_name="documentos")
    nome = models.CharField(max_length=200)
    arquivo = models.FileField(upload_to="financeiro/contas_receber/")
    tipo_arquivo = models.CharField(max_length=10, blank=True)
    tamanho_bytes = models.PositiveBigIntegerField(default=0)
    enviado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Documento de Conta a Receber"


class HistoricoPagamentoCliente(ModeloBase):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="historico_pagamento_cliente")
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="historico_pagamentos")
    conta_receber = models.ForeignKey(ContaReceber, on_delete=models.CASCADE)
    valor_pago = models.DecimalField(max_digits=15, decimal_places=2)
    data_pagamento = models.DateField()
    dias_atraso = models.SmallIntegerField(default=0)

    class Meta:
        verbose_name = "Histórico de Pagamento do Cliente"
        ordering = ["-data_pagamento"]


# ══════════════════════════════════════════════
# LANÇAMENTOS (FLUXO DE CAIXA)
# ══════════════════════════════════════════════

class LancamentoFinanceiro(ModeloBase):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="lancamentos")
    conta_bancaria = models.ForeignKey(ContaBancaria, on_delete=models.PROTECT)
    tipo_lancamento = models.ForeignKey(TipoLancamento, on_delete=models.PROTECT)
    plano_contas = models.ForeignKey(PlanoContas, on_delete=models.PROTECT, null=True, blank=True)
    centro_custo = models.ForeignKey(CentroCusto, on_delete=models.SET_NULL, null=True, blank=True)
    conta_pagar = models.ForeignKey(ContaPagar, on_delete=models.SET_NULL, null=True, blank=True)
    conta_receber = models.ForeignKey(ContaReceber, on_delete=models.SET_NULL, null=True, blank=True)
    descricao = models.CharField(max_length=300)
    valor = models.DecimalField(max_digits=15, decimal_places=2)
    data_lancamento = models.DateField()
    data_competencia = models.DateField(null=True, blank=True)
    conciliado = models.BooleanField(default=False)
    numero_documento = models.CharField(max_length=100, blank=True)
    observacoes = models.TextField(blank=True)
    criado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Lançamento Financeiro"
        verbose_name_plural = "Lançamentos Financeiros"
        ordering = ["-data_lancamento"]


class TransferenciaBancaria(ModeloBase):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="transferencias_bancarias")
    conta_origem = models.ForeignKey(ContaBancaria, on_delete=models.PROTECT, related_name="transferencias_saida")
    conta_destino = models.ForeignKey(ContaBancaria, on_delete=models.PROTECT, related_name="transferencias_entrada")
    valor = models.DecimalField(max_digits=15, decimal_places=2)
    data_transferencia = models.DateField()
    descricao = models.CharField(max_length=300, blank=True)
    lancamento_debito = models.OneToOneField(
        LancamentoFinanceiro, on_delete=models.SET_NULL, null=True, related_name="transferencia_debito"
    )
    lancamento_credito = models.OneToOneField(
        LancamentoFinanceiro, on_delete=models.SET_NULL, null=True, related_name="transferencia_credito"
    )
    criado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Transferência Bancária"


class ProjecaoFluxoCaixa(ModeloBase):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="projecoes_fluxo")
    conta_bancaria = models.ForeignKey(ContaBancaria, on_delete=models.SET_NULL, null=True, blank=True)
    cenario = models.ForeignKey(TipoCenarioFluxo, on_delete=models.PROTECT)
    data_referencia = models.DateField()
    entradas_previstas = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    saidas_previstas = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    saldo_projetado = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    gerado_automaticamente = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Projeção de Fluxo de Caixa"
        ordering = ["data_referencia"]