from django.db import models
from apps.authentication.models import ModeloBase, Empresa, Usuario
from apps.sistema.models import ContaBancaria
from apps.financeiro.models import LancamentoFinanceiro


# ══════════════════════════════════════════════
# CHOICES CADASTRÁVEIS
# ══════════════════════════════════════════════

class TipoArquivoBancario(ModeloBase):
    """Ex: OFX, CNAB 240, CNAB 150, CSV"""
    nome = models.CharField(max_length=50, unique=True)
    extensao = models.CharField(max_length=10)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Arquivo Bancário"


class StatusConciliacao(ModeloBase):
    """Ex: Pendente, Conciliada, Divergente, Ignorada"""
    nome = models.CharField(max_length=50, unique=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Status de Conciliação"


class TipoMovimentoBancario(ModeloBase):
    """Ex: Crédito, Débito, Tarifa, Saldo, Transferência, PIX"""
    nome = models.CharField(max_length=100, unique=True)
    natureza = models.CharField(max_length=1, choices=[("D", "Débito"), ("C", "Crédito")])
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Movimento Bancário"


# ══════════════════════════════════════════════
# EXTRATO BANCÁRIO
# ══════════════════════════════════════════════

class ImportacaoExtrato(ModeloBase):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="importacoes_extrato")
    conta_bancaria = models.ForeignKey(ContaBancaria, on_delete=models.PROTECT)
    tipo_arquivo = models.ForeignKey(TipoArquivoBancario, on_delete=models.PROTECT)
    arquivo = models.FileField(upload_to="bancario/extratos/")
    nome_arquivo = models.CharField(max_length=200)
    data_inicio_extrato = models.DateField(null=True, blank=True)
    data_fim_extrato = models.DateField(null=True, blank=True)
    total_registros = models.PositiveIntegerField(default=0)
    total_conciliados = models.PositiveIntegerField(default=0)
    total_divergentes = models.PositiveIntegerField(default=0)
    importado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    processado = models.BooleanField(default=False)
    log_processamento = models.TextField(blank=True)

    class Meta:
        verbose_name = "Importação de Extrato"
        ordering = ["-criado_em"]


class MovimentoBancario(ModeloBase):
    importacao = models.ForeignKey(ImportacaoExtrato, on_delete=models.CASCADE, related_name="movimentos")
    conta_bancaria = models.ForeignKey(ContaBancaria, on_delete=models.PROTECT)
    tipo_movimento = models.ForeignKey(TipoMovimentoBancario, on_delete=models.SET_NULL, null=True, blank=True)
    data_movimento = models.DateField()
    data_lancamento = models.DateField(null=True, blank=True)
    valor = models.DecimalField(max_digits=15, decimal_places=2)
    descricao = models.CharField(max_length=500)
    documento = models.CharField(max_length=100, blank=True)
    numero_banco = models.CharField(max_length=50, blank=True)
    saldo_apos = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    status_conciliacao = models.ForeignKey(StatusConciliacao, on_delete=models.PROTECT, null=True)

    class Meta:
        verbose_name = "Movimento Bancário"
        ordering = ["data_movimento"]


# ══════════════════════════════════════════════
# CONCILIAÇÃO
# ══════════════════════════════════════════════

class ConciliacaoBancaria(ModeloBase):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="conciliacoes")
    movimento_bancario = models.ForeignKey(MovimentoBancario, on_delete=models.CASCADE, related_name="conciliacoes")
    lancamento = models.ForeignKey(LancamentoFinanceiro, on_delete=models.CASCADE, related_name="conciliacoes")
    status = models.ForeignKey(StatusConciliacao, on_delete=models.PROTECT)
    automatica = models.BooleanField(default=False)
    diferenca = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    observacao = models.TextField(blank=True)
    conciliado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Conciliação Bancária"
        ordering = ["-criado_em"]


class DivergenciaConciliacao(ModeloBase):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="divergencias_conciliacao")
    movimento_bancario = models.ForeignKey(MovimentoBancario, on_delete=models.CASCADE, null=True, blank=True)
    lancamento = models.ForeignKey(LancamentoFinanceiro, on_delete=models.CASCADE, null=True, blank=True)
    tipo_divergencia = models.CharField(
        max_length=30,
        choices=[
            ("SEM_LANCAMENTO", "Movimento sem lançamento"),
            ("SEM_MOVIMENTO", "Lançamento sem movimento"),
            ("VALOR_DIFERENTE", "Valores divergentes"),
            ("DATA_DIFERENTE", "Datas divergentes"),
        ]
    )
    valor_extrato = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    valor_sistema = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    resolvida = models.BooleanField(default=False)
    resolucao = models.TextField(blank=True)

    class Meta:
        verbose_name = "Divergência de Conciliação"


# ══════════════════════════════════════════════
# REMESSA E RETORNO
# ══════════════════════════════════════════════

class ArquivoRemessa(ModeloBase):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="arquivos_remessa")
    conta_bancaria = models.ForeignKey(ContaBancaria, on_delete=models.PROTECT)
    tipo = models.CharField(max_length=20, choices=[("PAGAMENTO", "Pagamento"), ("COBRANCA", "Cobrança")])
    nome_arquivo = models.CharField(max_length=200)
    arquivo = models.FileField(upload_to="bancario/remessas/", null=True, blank=True)
    numero_sequencial = models.PositiveIntegerField(default=1)
    total_registros = models.PositiveIntegerField(default=0)
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    enviado = models.BooleanField(default=False)
    data_envio = models.DateField(null=True, blank=True)
    gerado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Arquivo de Remessa"


class ArquivoRetorno(ModeloBase):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="arquivos_retorno")
    conta_bancaria = models.ForeignKey(ContaBancaria, on_delete=models.PROTECT)
    arquivo_remessa = models.ForeignKey(ArquivoRemessa, on_delete=models.SET_NULL, null=True, blank=True)
    nome_arquivo = models.CharField(max_length=200)
    arquivo = models.FileField(upload_to="bancario/retornos/")
    total_registros = models.PositiveIntegerField(default=0)
    total_processados = models.PositiveIntegerField(default=0)
    total_rejeitados = models.PositiveIntegerField(default=0)
    processado = models.BooleanField(default=False)
    importado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Arquivo de Retorno"