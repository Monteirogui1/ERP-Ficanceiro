from django.urls import path
from . import views

app_name = "fiscal"

urlpatterns = [

    # ── Tabelas de Domínio ───────────────────

    # Tipo de Imposto
    path("dominios/tipos-imposto/", views.TipoImpostoListView.as_view(), name="tipo_imposto_list"),
    path("dominios/tipos-imposto/novo/", views.TipoImpostoCreateView.as_view(), name="tipo_imposto_create"),
    path("dominios/tipos-imposto/<int:pk>/editar/", views.TipoImpostoUpdateView.as_view(), name="tipo_imposto_update"),
    path("dominios/tipos-imposto/<int:pk>/excluir/", views.TipoImpostoDeleteView.as_view(), name="tipo_imposto_delete"),

    # Tipo de Obrigação Fiscal
    path("dominios/tipos-obrigacao/", views.TipoObrigacaoFiscalListView.as_view(), name="tipo_obrigacao_list"),
    path("dominios/tipos-obrigacao/novo/", views.TipoObrigacaoFiscalCreateView.as_view(), name="tipo_obrigacao_create"),
    path("dominios/tipos-obrigacao/<int:pk>/editar/", views.TipoObrigacaoFiscalUpdateView.as_view(), name="tipo_obrigacao_update"),
    path("dominios/tipos-obrigacao/<int:pk>/excluir/", views.TipoObrigacaoFiscalDeleteView.as_view(), name="tipo_obrigacao_delete"),

    # Status de Obrigação Fiscal
    path("dominios/status-obrigacao/", views.StatusObrigacaoFiscalListView.as_view(), name="status_obrigacao_list"),
    path("dominios/status-obrigacao/novo/", views.StatusObrigacaoFiscalCreateView.as_view(), name="status_obrigacao_create"),
    path("dominios/status-obrigacao/<int:pk>/editar/", views.StatusObrigacaoFiscalUpdateView.as_view(), name="status_obrigacao_update"),
    path("dominios/status-obrigacao/<int:pk>/excluir/", views.StatusObrigacaoFiscalDeleteView.as_view(), name="status_obrigacao_delete"),

    # ── Configuração de Impostos ─────────────
    path("configuracoes/", views.ConfiguracaoImpostoListView.as_view(), name="configuracao_imposto_list"),
    path("configuracoes/nova/", views.ConfiguracaoImpostoCreateView.as_view(), name="configuracao_imposto_create"),
    path("configuracoes/<int:pk>/editar/", views.ConfiguracaoImpostoUpdateView.as_view(), name="configuracao_imposto_update"),
    path("configuracoes/<int:pk>/excluir/", views.ConfiguracaoImpostoDeleteView.as_view(), name="configuracao_imposto_delete"),

    # ── Lançamentos de Impostos ──────────────
    path("lancamentos/", views.LancamentoImpostoListView.as_view(), name="lancamento_imposto_list"),
    path("lancamentos/novo/", views.LancamentoImpostoCreateView.as_view(), name="lancamento_imposto_create"),
    path("lancamentos/<int:pk>/editar/", views.LancamentoImpostoUpdateView.as_view(), name="lancamento_imposto_update"),
    path("lancamentos/<int:pk>/excluir/", views.LancamentoImpostoDeleteView.as_view(), name="lancamento_imposto_delete"),

    # ── Obrigações Fiscais ───────────────────
    path("obrigacoes/", views.ObrigacaoFiscalListView.as_view(), name="obrigacao_list"),
    path("obrigacoes/nova/", views.ObrigacaoFiscalCreateView.as_view(), name="obrigacao_create"),
    path("obrigacoes/<int:pk>/", views.ObrigacaoFiscalDetailView.as_view(), name="obrigacao_detail"),
    path("obrigacoes/<int:pk>/editar/", views.ObrigacaoFiscalUpdateView.as_view(), name="obrigacao_update"),
    path("obrigacoes/<int:pk>/excluir/", views.ObrigacaoFiscalDeleteView.as_view(), name="obrigacao_delete"),
]