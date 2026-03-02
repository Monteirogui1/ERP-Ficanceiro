from django.urls import path
from . import views

app_name = "bancario"

urlpatterns = [

    # ── Tabelas de Domínio ───────────────────

    # Tipo de Arquivo Bancário
    path("dominios/tipos-arquivo/", views.TipoArquivoBancarioListView.as_view(), name="tipo_arquivo_list"),
    path("dominios/tipos-arquivo/novo/", views.TipoArquivoBancarioCreateView.as_view(), name="tipo_arquivo_create"),
    path("dominios/tipos-arquivo/<int:pk>/editar/", views.TipoArquivoBancarioUpdateView.as_view(), name="tipo_arquivo_update"),
    path("dominios/tipos-arquivo/<int:pk>/excluir/", views.TipoArquivoBancarioDeleteView.as_view(), name="tipo_arquivo_delete"),

    # Status de Conciliação
    path("dominios/status-conciliacao/", views.StatusConciliacaoListView.as_view(), name="status_conciliacao_list"),
    path("dominios/status-conciliacao/novo/", views.StatusConciliacaoCreateView.as_view(), name="status_conciliacao_create"),
    path("dominios/status-conciliacao/<int:pk>/editar/", views.StatusConciliacaoUpdateView.as_view(), name="status_conciliacao_update"),
    path("dominios/status-conciliacao/<int:pk>/excluir/", views.StatusConciliacaoDeleteView.as_view(), name="status_conciliacao_delete"),

    # Tipo de Movimento Bancário
    path("dominios/tipos-movimento/", views.TipoMovimentoBancarioListView.as_view(), name="tipo_movimento_list"),
    path("dominios/tipos-movimento/novo/", views.TipoMovimentoBancarioCreateView.as_view(), name="tipo_movimento_create"),
    path("dominios/tipos-movimento/<int:pk>/editar/", views.TipoMovimentoBancarioUpdateView.as_view(), name="tipo_movimento_update"),
    path("dominios/tipos-movimento/<int:pk>/excluir/", views.TipoMovimentoBancarioDeleteView.as_view(), name="tipo_movimento_delete"),

    # ── Importação de Extratos ───────────────
    path("extratos/", views.ImportacaoExtratoListView.as_view(), name="importacao_list"),
    path("extratos/importar/", views.ImportacaoExtratoCreateView.as_view(), name="importacao_create"),
    path("extratos/<int:pk>/", views.ImportacaoExtratoDetailView.as_view(), name="importacao_detail"),

    # ── Conciliação Bancária ─────────────────
    path("conciliacao/", views.ConciliacaoBancariaListView.as_view(), name="conciliacao_list"),
    path("conciliacao/nova/", views.ConciliacaoBancariaCreateView.as_view(), name="conciliacao_create"),
    path("conciliacao/<int:pk>/excluir/", views.ConciliacaoBancariaDeleteView.as_view(), name="conciliacao_delete"),

    # ── Divergências ─────────────────────────
    path("divergencias/", views.DivergenciaConciliacaoListView.as_view(), name="divergencia_list"),
    path("divergencias/<int:pk>/resolver/", views.DivergenciaConciliacaoUpdateView.as_view(), name="divergencia_update"),

    # ── Remessa ──────────────────────────────
    path("remessas/", views.ArquivoRemessaListView.as_view(), name="remessa_list"),
    path("remessas/nova/", views.ArquivoRemessaCreateView.as_view(), name="remessa_create"),

    # ── Retorno ──────────────────────────────
    path("retornos/", views.ArquivoRetornoListView.as_view(), name="retorno_list"),
    path("retornos/importar/", views.ArquivoRetornoCreateView.as_view(), name="retorno_create"),
]