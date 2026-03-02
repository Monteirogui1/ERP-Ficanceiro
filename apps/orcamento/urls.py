from django.urls import path
from . import views

app_name = "orcamento"

urlpatterns = [

    # ── Tabelas de Domínio ───────────────────

    # Status de Orçamento
    path("dominios/status/", views.StatusOrcamentoListView.as_view(), name="status_list"),
    path("dominios/status/novo/", views.StatusOrcamentoCreateView.as_view(), name="status_create"),
    path("dominios/status/<int:pk>/editar/", views.StatusOrcamentoUpdateView.as_view(), name="status_update"),
    path("dominios/status/<int:pk>/excluir/", views.StatusOrcamentoDeleteView.as_view(), name="status_delete"),

    # ── Orçamentos ───────────────────────────
    path("", views.OrcamentoListView.as_view(), name="orcamento_list"),
    path("novo/", views.OrcamentoCreateView.as_view(), name="orcamento_create"),
    path("<int:pk>/", views.OrcamentoDetailView.as_view(), name="orcamento_detail"),
    path("<int:pk>/editar/", views.OrcamentoUpdateView.as_view(), name="orcamento_update"),
    path("<int:pk>/excluir/", views.OrcamentoDeleteView.as_view(), name="orcamento_delete"),

    # ── Itens de Orçamento ───────────────────
    path("<int:orcamento_pk>/itens/novo/", views.ItemOrcamentoCreateView.as_view(), name="item_create"),
    path("itens/<int:pk>/editar/", views.ItemOrcamentoUpdateView.as_view(), name="item_update"),
    path("itens/<int:pk>/excluir/", views.ItemOrcamentoDeleteView.as_view(), name="item_delete"),

    # ── Alertas de Estouro ───────────────────
    path("alertas/", views.AlertaEstouroOrcamentoListView.as_view(), name="alerta_list"),
]