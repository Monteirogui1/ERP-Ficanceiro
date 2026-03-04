from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "authentication"

urlpatterns = [

    # ── Autenticação ─────────────────────────
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="authentication/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="authentication:login"),
        name="logout",
    ),
    path(
        "senha/alterar/",
        auth_views.PasswordChangeView.as_view(
            template_name="authentication/password_change.html",
            success_url="/senha/alterar/concluido/",
        ),
        name="password_change",
    ),
    path(
        "senha/alterar/concluido/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="authentication/password_change_done.html"
        ),
        name="password_change_done",
    ),

    # ── Seleção de empresa ativa na sessão ───
    path("selecionar-empresa/", views.SelecionarEmpresaView.as_view(), name="selecionar_empresa"),

    # ── Dashboard / Home ─────────────────────
    path("", views.DashboardView.as_view(), name="dashboard"),

    # ── Empresas ─────────────────────────────
    path("empresas/", views.EmpresaListView.as_view(), name="empresa_list"),
    path("empresas/nova/", views.EmpresaCreateView.as_view(), name="empresa_create"),
    path("empresas/<int:pk>/editar/", views.EmpresaUpdateView.as_view(), name="empresa_update"),
    path("empresas/<int:pk>/excluir/", views.EmpresaDeleteView.as_view(), name="empresa_delete"),

    # ── Filiais ──────────────────────────────
    path("empresas/<int:empresa_pk>/filiais/", views.FilialListView.as_view(), name="filial_list"),
    path("empresas/<int:empresa_pk>/filiais/nova/", views.FilialCreateView.as_view(), name="filial_create"),
    path("filiais/<int:pk>/editar/", views.FilialUpdateView.as_view(), name="filial_update"),
    path("filiais/<int:pk>/excluir/", views.FilialDeleteView.as_view(), name="filial_delete"),

    # ── Usuários ─────────────────────────────
    path("usuarios/", views.UsuarioListView.as_view(), name="usuario_list"),
    path("usuarios/novo/", views.UsuarioCreateView.as_view(), name="usuario_create"),
    path("usuarios/<int:pk>/editar/", views.UsuarioUpdateView.as_view(), name="usuario_update"),
    path("usuarios/<int:pk>/excluir/", views.UsuarioDeleteView.as_view(), name="usuario_delete"),

    # ── Perfis de Acesso ─────────────────────
    path("perfis/", views.PerfilAcessoListView.as_view(), name="perfil_list"),
    path("perfis/novo/", views.PerfilAcessoCreateView.as_view(), name="perfil_create"),
    path("perfis/<int:pk>/editar/", views.PerfilAcessoUpdateView.as_view(), name="perfil_update"),
    path("perfis/<int:pk>/excluir/", views.PerfilAcessoDeleteView.as_view(), name="perfil_delete"),

    # ── Tabelas de Domínio ───────────────────
    path("dominios/segmentos/", views.SegmentoEmpresaListView.as_view(), name="segmento_list"),
    path("dominios/segmentos/novo/", views.SegmentoEmpresaCreateView.as_view(), name="segmento_create"),
    path("dominios/segmentos/<int:pk>/editar/", views.SegmentoEmpresaUpdateView.as_view(), name="segmento_update"),
    path("dominios/segmentos/<int:pk>/excluir/", views.SegmentoEmpresaDeleteView.as_view(), name="segmento_delete"),

    path("dominios/regimes/", views.RegimeTributarioListView.as_view(), name="regime_list"),
    path("dominios/regimes/novo/", views.RegimeTributarioCreateView.as_view(), name="regime_create"),
    path("dominios/regimes/<int:pk>/editar/", views.RegimeTributarioUpdateView.as_view(), name="regime_update"),
    path("dominios/regimes/<int:pk>/excluir/", views.RegimeTributarioDeleteView.as_view(), name="regime_delete"),

    path("dominios/tipos-documento/", views.TipoDocumentoListView.as_view(), name="tipo_documento_list"),
    path("dominios/tipos-documento/novo/", views.TipoDocumentoCreateView.as_view(), name="tipo_documento_create"),
    path("dominios/tipos-documento/<int:pk>/editar/", views.TipoDocumentoUpdateView.as_view(), name="tipo_documento_update"),
    path("dominios/tipos-documento/<int:pk>/excluir/", views.TipoDocumentoDeleteView.as_view(), name="tipo_documento_delete"),

    path("dominios/tipos-contato/", views.TipoContatoListView.as_view(), name="tipo_contato_list"),
    path("dominios/tipos-contato/novo/", views.TipoContatoCreateView.as_view(), name="tipo_contato_create"),
    path("dominios/tipos-contato/<int:pk>/editar/", views.TipoContatoUpdateView.as_view(), name="tipo_contato_update"),
    path("dominios/tipos-contato/<int:pk>/excluir/", views.TipoContatoDeleteView.as_view(), name="tipo_contato_delete"),

    path("dominios/tipos-notificacao/", views.TipoNotificacaoListView.as_view(), name="tipo_notificacao_list"),
    path("dominios/tipos-notificacao/novo/", views.TipoNotificacaoCreateView.as_view(), name="tipo_notificacao_create"),
    path("dominios/tipos-notificacao/<int:pk>/editar/", views.TipoNotificacaoUpdateView.as_view(), name="tipo_notificacao_update"),
    path("dominios/tipos-notificacao/<int:pk>/excluir/", views.TipoNotificacaoDeleteView.as_view(), name="tipo_notificacao_delete"),

    # ── Logs e Notificações ──────────────────
    path("logs/", views.LogAuditoriaListView.as_view(), name="log_list"),
    path("notificacoes/", views.NotificacaoListView.as_view(), name="notificacao_list"),
    path("notificacoes/<int:pk>/marcar-lida/", views.NotificacaoMarcarLidaView.as_view(), name="notificacao_marcar_lida"),
]