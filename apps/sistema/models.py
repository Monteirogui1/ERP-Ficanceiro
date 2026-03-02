from django.db import models
from apps.authentication.models import ModeloBase, Empresa, FilialEmpresa, TipoContato


# ══════════════════════════════════════════════
# CHOICES CADASTRÁVEIS
# ══════════════════════════════════════════════

class TipoPessoa(ModeloBase):
    """Ex: Física, Jurídica, Estrangeira"""
    nome = models.CharField(max_length=50, unique=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Pessoa"


class CategoriaFornecedor(ModeloBase):
    """Ex: Serviços, Materiais, Utilidades, Tecnologia, Logística"""
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="categorias_fornecedor")
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Categoria de Fornecedor"
        unique_together = ("empresa", "nome")


class CategoriaCliente(ModeloBase):
    """Ex: Pessoa Física, Pessoa Jurídica, Governo, Revendedor"""
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="categorias_cliente")
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Categoria de Cliente"
        unique_together = ("empresa", "nome")


class TipoConta(ModeloBase):
    """Ex: Conta Corrente, Conta Poupança, Conta Investimento, Caixa"""
    nome = models.CharField(max_length=100, unique=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Conta Bancária"


class TipoChavePix(ModeloBase):
    """Ex: CPF, CNPJ, E-mail, Telefone, Chave Aleatória"""
    nome = models.CharField(max_length=50, unique=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Chave PIX"


class TipoPlanoContas(ModeloBase):
    """Ex: Receita, Despesa, Ativo, Passivo, Patrimônio Líquido"""
    nome = models.CharField(max_length=100, unique=True)
    natureza = models.CharField(
        max_length=1,
        choices=[("D", "Devedora"), ("C", "Credora")],
        default="D"
    )
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Plano de Contas"


class TipoCentroCusto(ModeloBase):
    """Ex: Departamento, Projeto, Unidade de Negócio, Filial, Produto"""
    nome = models.CharField(max_length=100, unique=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Centro de Custo"


# ══════════════════════════════════════════════
# FORNECEDORES
# ══════════════════════════════════════════════

class Fornecedor(ModeloBase):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="fornecedores")
    tipo_pessoa = models.ForeignKey(TipoPessoa, on_delete=models.PROTECT, null=True)
    categoria = models.ForeignKey(CategoriaFornecedor, on_delete=models.SET_NULL, null=True, blank=True)
    razao_social = models.CharField(max_length=200)
    nome_fantasia = models.CharField(max_length=200, blank=True)
    cpf_cnpj = models.CharField(max_length=18)
    inscricao_estadual = models.CharField(max_length=30, blank=True)
    inscricao_municipal = models.CharField(max_length=30, blank=True)
    cep = models.CharField(max_length=9, blank=True)
    logradouro = models.CharField(max_length=200, blank=True)
    numero = models.CharField(max_length=20, blank=True)
    complemento = models.CharField(max_length=100, blank=True)
    bairro = models.CharField(max_length=100, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)
    pais = models.CharField(max_length=50, default="Brasil")
    prazo_padrao_pagamento = models.PositiveSmallIntegerField(default=30)
    limite_credito = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    observacoes = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Fornecedor"
        unique_together = ("empresa", "cpf_cnpj")


class ContatoFornecedor(ModeloBase):
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name="contatos")
    tipo = models.ForeignKey(TipoContato, on_delete=models.PROTECT)
    valor = models.CharField(max_length=200)
    responsavel = models.CharField(max_length=100, blank=True)
    principal = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Contato do Fornecedor"


# ══════════════════════════════════════════════
# CLIENTES
# ══════════════════════════════════════════════

class Cliente(ModeloBase):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="clientes")
    tipo_pessoa = models.ForeignKey(TipoPessoa, on_delete=models.PROTECT, null=True)
    categoria = models.ForeignKey(CategoriaCliente, on_delete=models.SET_NULL, null=True, blank=True)
    razao_social = models.CharField(max_length=200)
    nome_fantasia = models.CharField(max_length=200, blank=True)
    cpf_cnpj = models.CharField(max_length=18)
    inscricao_estadual = models.CharField(max_length=30, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    cep = models.CharField(max_length=9, blank=True)
    logradouro = models.CharField(max_length=200, blank=True)
    numero = models.CharField(max_length=20, blank=True)
    complemento = models.CharField(max_length=100, blank=True)
    bairro = models.CharField(max_length=100, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)
    pais = models.CharField(max_length=50, default="Brasil")
    limite_credito = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    prazo_padrao_recebimento = models.PositiveSmallIntegerField(default=30)
    score_credito = models.PositiveSmallIntegerField(null=True, blank=True)
    inadimplente = models.BooleanField(default=False)
    observacoes = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Cliente"
        unique_together = ("empresa", "cpf_cnpj")


class ContatoCliente(ModeloBase):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="contatos")
    tipo = models.ForeignKey(TipoContato, on_delete=models.PROTECT)
    valor = models.CharField(max_length=200)
    responsavel = models.CharField(max_length=100, blank=True)
    principal = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Contato do Cliente"


# ══════════════════════════════════════════════
# BANCOS E CONTAS BANCÁRIAS
# ══════════════════════════════════════════════

class Banco(ModeloBase):
    """Tabela de bancos — código FEBRABAN."""
    codigo = models.CharField(max_length=10, unique=True)
    nome = models.CharField(max_length=200)
    ispb = models.CharField(max_length=8, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Banco"
        ordering = ["codigo"]


class ContaBancaria(ModeloBase):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="contas_bancarias")
    filial = models.ForeignKey(FilialEmpresa, on_delete=models.SET_NULL, null=True, blank=True)
    banco = models.ForeignKey(Banco, on_delete=models.PROTECT)
    tipo_conta = models.ForeignKey(TipoConta, on_delete=models.PROTECT)
    nome = models.CharField(max_length=100)
    agencia = models.CharField(max_length=10)
    agencia_dv = models.CharField(max_length=2, blank=True)
    conta = models.CharField(max_length=20)
    conta_dv = models.CharField(max_length=2, blank=True)
    convenio = models.CharField(max_length=30, blank=True)
    carteira = models.CharField(max_length=10, blank=True)
    saldo_inicial = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    data_saldo_inicial = models.DateField(null=True, blank=True)
    saldo_atual = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    chave_pix = models.CharField(max_length=200, blank=True)
    tipo_chave_pix = models.ForeignKey(TipoChavePix, on_delete=models.SET_NULL, null=True, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Conta Bancária"


# ══════════════════════════════════════════════
# PLANO DE CONTAS
# ══════════════════════════════════════════════

class PlanoContas(ModeloBase):
    """Estrutura hierárquica de plano de contas contábil/gerencial."""
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="plano_contas")
    tipo = models.ForeignKey(TipoPlanoContas, on_delete=models.PROTECT)
    codigo = models.CharField(max_length=30, help_text="Ex: 1.1.01.001")
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    conta_pai = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="subcontas"
    )
    nivel = models.PositiveSmallIntegerField(default=1)
    analitica = models.BooleanField(default=True, help_text="False = conta sintética (só agrupa)")
    aceita_lancamentos = models.BooleanField(default=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Plano de Contas"
        unique_together = ("empresa", "codigo")
        ordering = ["codigo"]


# ══════════════════════════════════════════════
# CENTRO DE CUSTO
# ══════════════════════════════════════════════

class CentroCusto(ModeloBase):
    """Centro de custo/receita — departamento, projeto, unidade, filial."""
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="centros_custo")
    tipo = models.ForeignKey(TipoCentroCusto, on_delete=models.PROTECT)
    codigo = models.CharField(max_length=30)
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    responsavel = models.CharField(max_length=200, blank=True)
    centro_pai = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="subcentros"
    )
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Centro de Custo"
        unique_together = ("empresa", "codigo")
        ordering = ["codigo"]