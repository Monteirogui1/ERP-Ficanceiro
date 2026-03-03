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
# TABELAS DE DOMÍNIO
# 

class SegmentoEmpresa(ModeloBase):
    """Ex: Comércio, Indústria, Serviços, Agronegócio"""
    nome = models.CharField(max_length=100, unique=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Segmento de Empresa"

    def __str__(self):
        return self.nome


class RegimeTributario(ModeloBase):
    """Ex: Simples Nacional, Lucro Presumido, Lucro Real, MEI"""
    nome = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=10, unique=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Regime Tributário"

    def __str__(self):
        return f"{self.codigo} — {self.nome}"


class TipoDocumento(ModeloBase):
    """Ex: CPF, CNPJ, RG, Passaporte"""
    empresa = models.ForeignKey(
        "Empresa", on_delete=models.CASCADE, related_name="tipos_documento"
    )
    nome = models.CharField(max_length=50)
    sigla = models.CharField(max_length=10)
    mascara = models.CharField(max_length=30, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Documento"
        unique_together = ("empresa", "sigla")

    def __str__(self):
        return self.sigla


class TipoContato(ModeloBase):
    """Ex: Celular, Telefone Fixo, E-mail, WhatsApp"""
    empresa = models.ForeignKey(
        "Empresa", on_delete=models.CASCADE, related_name="tipos_contato"
    )
    nome = models.CharField(max_length=50)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Contato"

    def __str__(self):
        return self.nome


class TipoAcaoLog(ModeloBase):
    """Ex: LOGIN, LOGOUT, CRIAÇÃO, EDIÇÃO, EXCLUSÃO, APROVAÇÃO, EXPORTAÇÃO"""
    nome = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True)

    class Meta:
        verbose_name = "Tipo de Ação (Log)"

    def __str__(self):
        return self.nome


class TipoNotificacao(ModeloBase):
    """Ex: Alerta de Vencimento, Aprovação Pendente, Inadimplência"""
    nome = models.CharField(max_length=100, unique=True)
    icone = models.CharField(max_length=50, blank=True, help_text="Classe Bootstrap Icon. Ex: bi-bell")
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Notificação"

    def __str__(self):
        return self.nome


# 
# EMPRESA E FILIAIS
# 

class Empresa(ModeloBase):
    razao_social = models.CharField(max_length=200)
    nome_fantasia = models.CharField(max_length=200, blank=True)
    cnpj = models.CharField(max_length=18, unique=True, blank=True)
    inscricao_estadual = models.CharField(max_length=30, blank=True)
    inscricao_municipal = models.CharField(max_length=30, blank=True)
    segmento = models.ForeignKey(
        SegmentoEmpresa, on_delete=models.SET_NULL, null=True, blank=True
    )
    regime_tributario = models.ForeignKey(
        RegimeTributario, on_delete=models.SET_NULL, null=True, blank=True
    )
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
    logo = models.ImageField(upload_to="empresas/logos/", null=True, blank=True)
    plano = models.CharField(max_length=50, blank=True)
    data_vencimento_plano = models.DateField(null=True, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Empresa"

    def __str__(self):
        return self.nome_fantasia or self.razao_social


class FilialEmpresa(ModeloBase):
    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, related_name="filiais"
    )
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

    def __str__(self):
        return f"{self.nome} ({self.empresa.razao_social})"


# 
# USUÁRIOS E PERMISSÕES
# 

class PerfilAcesso(ModeloBase):
    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, related_name="perfis_acesso"
    )
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    permissoes = models.JSONField(
        default=dict,
        help_text=(
            "Ex: {'contas_pagar': {'ver': true, 'criar': true, "
            "'editar': false, 'excluir': false}}"
        ),
    )
    pode_aprovar_pagamentos = models.BooleanField(default=False)
    nivel_aprovacao = models.PositiveSmallIntegerField(
        default=1,
        help_text="Nível na cadeia de aprovação multinível",
    )
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Perfil de Acesso"
        unique_together = ("empresa", "nome")

    def __str__(self):
        return f"{self.nome} ({self.empresa.razao_social})"


class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O e-mail é obrigatório.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superusuário deve ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusuário deve ter is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Usuário central — pode acessar múltiplas empresas com perfis distintos.

    Os campos `groups` e `user_permissions` são redeclarados com related_name
    únicos para evitar conflito de reverse accessor com `auth.User`
    (E304: clashes with reverse accessor).

    ⚠️  settings.py DEVE conter:  AUTH_USER_MODEL = "authentication.Usuario"
    """

    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=200)
    empresa_principal = models.ForeignKey(
        Empresa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usuarios_principais",
    )
    perfil_acesso = models.ForeignKey(
        PerfilAcesso,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
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

    # ── Correção E304 ────────────────────────────────────────────────────────
    # PermissionsMixin declara esses campos sem related_name, gerando conflito
    # quando AUTH_USER_MODEL não é configurado (Django usa auth.User em paralelo).
    # A solução definitiva é redeclarar os campos com related_name únicos
    # E garantir AUTH_USER_MODEL = "authentication.Usuario" no settings.py.
    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="grupos",
        blank=True,
        related_name="usuario_set",          # evita clash com auth.User.groups
        related_query_name="usuario",
        help_text=(
            "Os grupos aos quais este usuário pertence. "
            "Um usuário obtém todas as permissões dos seus grupos."
        ),
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name="permissões do usuário",
        blank=True,
        related_name="usuario_set",          # evita clash com auth.User.user_permissions
        related_query_name="usuario",
        help_text="Permissões específicas para este usuário.",
    )
    # ────────────────────────────────────────────────────────────────────────

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome"]

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        return f"{self.nome} <{self.email}>"

    def get_full_name(self):
        return self.nome

    def get_short_name(self):
        return self.nome.split()[0]


class UsuarioEmpresa(ModeloBase):
    """Vínculo M2M entre usuário e empresa com perfil por empresa."""
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="empresas_acesso"
    )
    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, related_name="usuarios_vinculados"
    )
    perfil_acesso = models.ForeignKey(
        PerfilAcesso, on_delete=models.SET_NULL, null=True, blank=True
    )
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Usuário × Empresa"
        unique_together = ("usuario", "empresa")

    def __str__(self):
        return f"{self.usuario.nome} @ {self.empresa.razao_social}"


# 
# AUDITORIA E NOTIFICAÇÕES
# 

class LogAuditoria(models.Model):
    """
    Registro imutável — não herda ModeloBase para não ter `atualizado_em`,
    pois logs nunca devem ser modificados.
    """
    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, related_name="logs_auditoria"
    )
    usuario = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True
    )
    tipo_acao = models.ForeignKey(
        TipoAcaoLog, on_delete=models.PROTECT
    )
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

    def __str__(self):
        return f"[{self.tipo_acao}] {self.usuario} — {self.modulo} ({self.criado_em:%d/%m/%Y %H:%M})"


class Notificacao(ModeloBase):
    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, related_name="notificacoes"
    )
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="notificacoes"
    )
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

    def __str__(self):
        status = "✓" if self.lida else "●"
        return f"{status} {self.titulo} → {self.usuario.nome}"