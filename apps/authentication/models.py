from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


# 
# CLASSE BASE ABSTRATA
# 

class ModeloBase(models.Model):
    """Classe base com auditoria de criação e atualização para todos os models."""
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# 
# CHOICES CADASTRÁVEIS — TABELAS DE DOMÍNIO
# 

class SegmentoEmpresa(ModeloBase):
    """Ex: Comércio, Indústria, Serviços, Agronegócio"""
    nome = models.CharField(max_length=100, unique=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Segmento de Empresa"


class RegimeTributario(ModeloBase):
    """Ex: Simples Nacional, Lucro Presumido, Lucro Real, MEI"""
    nome = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=10, unique=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Regime Tributário"


class TipoDocumento(ModeloBase):
    """Ex: CPF, CNPJ, RG, Passaporte"""
    empresa = models.ForeignKey("Empresa", on_delete=models.CASCADE, related_name="tipos_documento")
    nome = models.CharField(max_length=50)
    sigla = models.CharField(max_length=10)
    mascara = models.CharField(max_length=30, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Documento"
        unique_together = ("empresa", "sigla")


class TipoContato(ModeloBase):
    """Ex: Celular, Telefone Fixo, E-mail, WhatsApp"""
    empresa = models.ForeignKey("Empresa", on_delete=models.CASCADE, related_name="tipos_contato")
    nome = models.CharField(max_length=50)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Contato"


class TipoAcaoLog(ModeloBase):
    """Ex: LOGIN, LOGOUT, CRIAÇÃO, EDIÇÃO, EXCLUSÃO, APROVAÇÃO, EXPORTAÇÃO"""
    nome = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True)

    class Meta:
        verbose_name = "Tipo de Ação (Log)"


class TipoNotificacao(ModeloBase):
    """Ex: Vencimento, Inadimplência, Estouro de Orçamento, Aprovação Pendente"""
    nome = models.CharField(max_length=100, unique=True)
    icone = models.CharField(max_length=50, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Notificação"


# 
# EMPRESA (TENANT)
# 

class Empresa(ModeloBase):
    razao_social = models.CharField(max_length=200)
    nome_fantasia = models.CharField(max_length=200, blank=True)
    cnpj = models.CharField(max_length=18, unique=True)
    inscricao_estadual = models.CharField(max_length=30, blank=True)
    inscricao_municipal = models.CharField(max_length=30, blank=True)
    segmento = models.ForeignKey(SegmentoEmpresa, on_delete=models.SET_NULL, null=True, blank=True)
    regime_tributario = models.ForeignKey(RegimeTributario, on_delete=models.SET_NULL, null=True, blank=True)
    cep = models.CharField(max_length=9, blank=True)
    logradouro = models.CharField(max_length=200, blank=True)
    numero = models.CharField(max_length=20, blank=True)
    complemento = models.CharField(max_length=100, blank=True)
    bairro = models.CharField(max_length=100, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    site = models.URLField(blank=True)
    plano = models.CharField(max_length=50, blank=True)
    ativo = models.BooleanField(default=True)
    data_vencimento_plano = models.DateField(null=True, blank=True)
    logo = models.ImageField(upload_to="empresas/logos/", null=True, blank=True)

    class Meta:
        verbose_name = "Empresa"


class FilialEmpresa(ModeloBase):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="filiais")
    nome = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=18, blank=True)
    cep = models.CharField(max_length=9, blank=True)
    logradouro = models.CharField(max_length=200, blank=True)
    numero = models.CharField(max_length=20, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Filial"


# 
# USUÁRIOS E PERMISSÕES
# 

class PerfilAcesso(ModeloBase):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="perfis_acesso")
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    permissoes = models.JSONField(
        default=dict,
        help_text="{'contas_pagar': {'ver': true, 'criar': true, 'editar': false, 'excluir': false}}"
    )
    pode_aprovar_pagamentos = models.BooleanField(default=False)
    nivel_aprovacao = models.PositiveSmallIntegerField(
        default=1,
        help_text="Nível na cadeia de aprovação multinível"
    )
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Perfil de Acesso"
        unique_together = ("empresa", "nome")


class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Usuário central — pode acessar múltiplas empresas com perfis distintos.
    Não herda ModeloBase pois AbstractBaseUser já define seus próprios campos de tempo.
    """
    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=200)
    empresa_principal = models.ForeignKey(
        Empresa, on_delete=models.SET_NULL, null=True, blank=True, related_name="usuarios_principais"
    )
    perfil_acesso = models.ForeignKey(PerfilAcesso, on_delete=models.SET_NULL, null=True, blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="usuarios/avatares/", null=True, blank=True)
    dois_fatores_ativo = models.BooleanField(default=False)
    dois_fatores_secret = models.CharField(max_length=64, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    ultimo_acesso = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    objects = UsuarioManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome"]

    class Meta:
        verbose_name = "Usuário"


class UsuarioEmpresa(ModeloBase):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="empresas_acesso")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="usuarios_vinculados")
    perfil_acesso = models.ForeignKey(PerfilAcesso, on_delete=models.SET_NULL, null=True, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Usuário × Empresa"
        unique_together = ("usuario", "empresa")


# 
# AUDITORIA E NOTIFICAÇÕES
# 

class LogAuditoria(models.Model):
    """
    Registro imutável — não herda ModeloBase para não ter atualizado_em,
    pois logs nunca devem ser modificados.
    """
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="logs_auditoria")
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    tipo_acao = models.ForeignKey(TipoAcaoLog, on_delete=models.PROTECT)
    modulo = models.CharField(max_length=100)
    objeto_tipo = models.CharField(max_length=100, blank=True)
    objeto_id = models.PositiveBigIntegerField(null=True, blank=True)
    descricao = models.TextField(blank=True)
    dados_anteriores = models.JSONField(null=True, blank=True)
    dados_novos = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Log de Auditoria"
        ordering = ["-criado_em"]


class Notificacao(ModeloBase):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="notificacoes")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="notificacoes")
    tipo = models.ForeignKey(TipoNotificacao, on_delete=models.PROTECT)
    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()
    lida = models.BooleanField(default=False)
    data_leitura = models.DateTimeField(null=True, blank=True)
    objeto_tipo = models.CharField(max_length=100, blank=True)
    objeto_id = models.PositiveBigIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Notificação"
        ordering = ["-criado_em"]