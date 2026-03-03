from django.urls import path
from . import views

app_name = "home"

urlpatterns = [

    # ── Dashboard ────────────────────────────
    path("", views.DashboardView.as_view(), name="dashboard"),

    # ── Relatórios Gerenciais ────────────────
    path("relatorios/dre/", views.RelatorioDREView.as_view(), name="relatorio_dre"),
    path("relatorios/fluxo-caixa/", views.RelatorioFluxoCaixaView.as_view(), name="relatorio_fluxo_caixa"),
    path("relatorios/inadimplencia/", views.RelatorioInadimplenciaView.as_view(), name="relatorio_inadimplencia"),
    path("relatorios/centro-custo/", views.RelatorioCentroCustoView.as_view(), name="relatorio_centro_custo"),
    path("relatorios/contas-pagar/", views.RelatorioContasPagarView.as_view(), name="relatorio_contas_pagar"),
    path("relatorios/contas-receber/", views.RelatorioContasReceberView.as_view(), name="relatorio_contas_receber"),
    path("relatorios/impostos/", views.RelatorioImpostosView.as_view(), name="relatorio_impostos"),
]