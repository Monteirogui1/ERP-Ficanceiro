# admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    SegmentoEmpresa,
    RegimeTributario,
    TipoDocumento,
    TipoContato,
    TipoAcaoLog,
    TipoNotificacao,
    Empresa,
    FilialEmpresa,
    PerfilAcesso,
    Usuario,
    UsuarioEmpresa,
    LogAuditoria,
    Notificacao,
)


# ─────────────────────────────────────────────────────────────
# CONFIG BASE
# ─────────────────────────────────────────────────────────────

class ModeloBaseAdmin(admin.ModelAdmin):
    readonly_fields = ("criado_em", "atualizado_em")
    list_filter = ("ativo", "criado_em", "atualizado_em")
    search_fields = ("nome",)


# ─────────────────────────────────────────────────────────────
# DOMÍNIOS
# ─────────────────────────────────────────────────────────────

@admin.register(SegmentoEmpresa)
class SegmentoEmpresaAdmin(ModeloBaseAdmin):
    list_display = ("nome", "ativo", "criado_em")


@admin.register(RegimeTributario)
class RegimeTributarioAdmin(ModeloBaseAdmin):
    list_display = ("codigo", "nome", "ativo")
    search_fields = ("codigo", "nome")


@admin.register(TipoDocumento)
class TipoDocumentoAdmin(ModeloBaseAdmin):
    list_display = ("sigla", "nome", "empresa", "ativo")
    list_filter = ("empresa", "ativo")
    search_fields = ("sigla", "nome", "empresa__razao_social")


@admin.register(TipoContato)
class TipoContatoAdmin(ModeloBaseAdmin):
    list_display = ("nome", "empresa", "ativo")
    list_filter = ("empresa", "ativo")


@admin.register(TipoAcaoLog)
class TipoAcaoLogAdmin(admin.ModelAdmin):
    list_display = ("nome", "descricao", "criado_em")
    search_fields = ("nome",)


@admin.register(TipoNotificacao)
class TipoNotificacaoAdmin(ModeloBaseAdmin):
    list_display = ("nome", "icone", "ativo")
    search_fields = ("nome",)


# ─────────────────────────────────────────────────────────────
# EMPRESA
# ─────────────────────────────────────────────────────────────

class FilialInline(admin.TabularInline):
    model = FilialEmpresa
    extra = 0


@admin.register(Empresa)
class EmpresaAdmin(ModeloBaseAdmin):
    list_display = ("razao_social", "nome_fantasia", "cnpj", "segmento", "ativo")
    search_fields = ("razao_social", "nome_fantasia", "cnpj")
    list_filter = ("segmento", "regime_tributario", "ativo")
    inlines = [FilialInline]


@admin.register(FilialEmpresa)
class FilialEmpresaAdmin(ModeloBaseAdmin):
    list_display = ("nome", "empresa", "cnpj", "cidade", "estado", "ativo")
    list_filter = ("empresa", "estado", "ativo")
    search_fields = ("nome", "cnpj", "empresa__razao_social")


# ─────────────────────────────────────────────────────────────
# PERFIL
# ─────────────────────────────────────────────────────────────

@admin.register(PerfilAcesso)
class PerfilAcessoAdmin(ModeloBaseAdmin):
    list_display = (
        "nome",
        "empresa",
        "pode_aprovar_pagamentos",
        "nivel_aprovacao",
        "ativo",
    )
    list_filter = ("empresa", "ativo", "pode_aprovar_pagamentos")
    search_fields = ("nome", "empresa__razao_social")


# ─────────────────────────────────────────────────────────────
# USUÁRIO CUSTOM
# ─────────────────────────────────────────────────────────────

class UsuarioEmpresaInline(admin.TabularInline):
    model = UsuarioEmpresa
    extra = 0


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    ordering = ("email",)
    list_display = (
        "email",
        "nome",
        "empresa_principal",
        "perfil_acesso",
        "is_staff",
        "is_active",
    )
    search_fields = ("email", "nome")
    list_filter = ("is_staff", "is_active", "empresa_principal")

    readonly_fields = ("date_joined", "ultimo_acesso", "criado_em", "atualizado_em")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Informações Pessoais", {"fields": ("nome", "telefone", "avatar")}),
        (
            "Empresa & Perfil",
            {"fields": ("empresa_principal", "perfil_acesso")},
        ),
        (
            "Segurança",
            {
                "fields": (
                    "dois_fatores_ativo",
                    "dois_fatores_secret",
                )
            },
        ),
        (
            "Permissões",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Datas",
            {
                "fields": (
                    "date_joined",
                    "ultimo_acesso",
                    "criado_em",
                    "atualizado_em",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "nome", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )

    inlines = [UsuarioEmpresaInline]


@admin.register(UsuarioEmpresa)
class UsuarioEmpresaAdmin(ModeloBaseAdmin):
    list_display = ("usuario", "empresa", "perfil_acesso", "ativo")
    list_filter = ("empresa", "ativo")
    search_fields = ("usuario__nome", "empresa__razao_social")


# ─────────────────────────────────────────────────────────────
# LOGS
# ─────────────────────────────────────────────────────────────

@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display = (
        "tipo_acao",
        "usuario",
        "empresa",
        "modulo",
        "criado_em",
    )
    list_filter = ("empresa", "tipo_acao", "modulo", "criado_em")
    search_fields = ("usuario__nome", "modulo", "descricao")
    readonly_fields = [field.name for field in LogAuditoria._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ─────────────────────────────────────────────────────────────
# NOTIFICAÇÕES
# ─────────────────────────────────────────────────────────────

@admin.register(Notificacao)
class NotificacaoAdmin(ModeloBaseAdmin):
    list_display = (
        "titulo",
        "usuario",
        "empresa",
        "tipo",
        "lida",
        "criado_em",
    )
    list_filter = ("empresa", "tipo", "lida", "criado_em")
    search_fields = ("titulo", "mensagem", "usuario__nome")
