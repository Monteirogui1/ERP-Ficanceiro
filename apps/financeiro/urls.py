from django.urls import path
from . import views

app_name = "financeiro"

urlpatterns = [

    # ── Tabelas de Domínio ───────────────────

    # Tipo de Documento Financeiro
    path("dominios/tipos-documento/", views.TipoDocumentoFinanceiroListView.as_view(), name="tipo_documento_list"),
    path("dominios/tipos-documento/novo/", views.TipoDocumentoFinanceiroCreateView.as_view(), name="tipo_documento_create"),
    path("dominios/tipos-documento/<int:pk>/editar/", views.TipoDocumentoFinanceiroUpdateView.as_view(), name="tipo_documento_update"),
    path("dominios/tipos-documento/<int:pk>/excluir/", views.TipoDocumentoFinanceiroDeleteView.as_view(), name="tipo_documento_delete"),

    # Forma de Pagamento
    path("dominios/formas-pagamento/", views.FormaPagamentoListView.as_view(), name="forma_pagamento_list"),
    path("dominios/formas-pagamento/nova/", views.FormaPagamentoCreateView.as_view(), name="forma_pagamento_create"),
    path("dominios/formas-pagamento/<int:pk>/editar/", views.FormaPagamentoUpdateView.as_view(), name="forma_pagamento_update"),
    path("dominios/formas-pagamento/<int:pk>/excluir/", views.FormaPagamentoDeleteView.as_view(), name="forma_pagamento_delete"),

    # Status Conta a Pagar
    path("dominios/status-pagar/", views.StatusContaPagarListView.as_view(), name="status_conta_pagar_list"),
    path("dominios/status-pagar/novo/", views.StatusContaPagarCreateView.as_view(), name="status_conta_pagar_create"),
    path("dominios/status-pagar/<int:pk>/editar/", views.StatusContaPagarUpdateView.as_view(), name="status_conta_pagar_update"),
    path("dominios/status-pagar/<int:pk>/excluir/", views.StatusContaPagarDeleteView.as_view(), name="status_conta_pagar_delete"),

    # Status Conta a Receber
    path("dominios/status-receber/", views.StatusContaReceberListView.as_view(), name="status_conta_receber_list"),
    path("dominios/status-receber/novo/", views.StatusContaReceberCreateView.as_view(), name="status_conta_receber_create"),
    path("dominios/status-receber/<int:pk>/editar/", views.StatusContaReceberUpdateView.as_view(), name="status_conta_receber_update"),
    path("dominios/status-receber/<int:pk>/excluir/", views.StatusContaReceberDeleteView.as_view(), name="status_conta_receber_delete"),

    # Periodicidade de Recorrência
    path("dominios/periodicidades/", views.PeriodicidadeRecorrenciaListView.as_view(), name="periodicidade_list"),
    path("dominios/periodicidades/nova/", views.PeriodicidadeRecorrenciaCreateView.as_view(), name="periodicidade_create"),
    path("dominios/periodicidades/<int:pk>/editar/", views.PeriodicidadeRecorrenciaUpdateView.as_view(), name="periodicidade_update"),
    path("dominios/periodicidades/<int:pk>/excluir/", views.PeriodicidadeRecorrenciaDeleteView.as_view(), name="periodicidade_delete"),

    # Tipo de Encargo
    path("dominios/tipos-encargo/", views.TipoEncargoListView.as_view(), name="tipo_encargo_list"),
    path("dominios/tipos-encargo/novo/", views.TipoEncargoCreateView.as_view(), name="tipo_encargo_create"),
    path("dominios/tipos-encargo/<int:pk>/editar/", views.TipoEncargoUpdateView.as_view(), name="tipo_encargo_update"),
    path("dominios/tipos-encargo/<int:pk>/excluir/", views.TipoEncargoDeleteView.as_view(), name="tipo_encargo_delete"),

    # Tipo de Cenário de Fluxo
    path("dominios/cenarios-fluxo/", views.TipoCenarioFluxoListView.as_view(), name="tipo_cenario_fluxo_list"),
    path("dominios/cenarios-fluxo/novo/", views.TipoCenarioFluxoCreateView.as_view(), name="tipo_cenario_fluxo_create"),
    path("dominios/cenarios-fluxo/<int:pk>/editar/", views.TipoCenarioFluxoUpdateView.as_view(), name="tipo_cenario_fluxo_update"),
    path("dominios/cenarios-fluxo/<int:pk>/excluir/", views.TipoCenarioFluxoDeleteView.as_view(), name="tipo_cenario_fluxo_delete"),

    # ── Contas a Pagar ───────────────────────
    path("contas-pagar/", views.ContaPagarListView.as_view(), name="conta_pagar_list"),
    path("contas-pagar/nova/", views.ContaPagarCreateView.as_view(), name="conta_pagar_create"),
    path("contas-pagar/<int:pk>/", views.ContaPagarDetailView.as_view(), name="conta_pagar_detail"),
    path("contas-pagar/<int:pk>/editar/", views.ContaPagarUpdateView.as_view(), name="conta_pagar_update"),
    path("contas-pagar/<int:pk>/excluir/", views.ContaPagarDeleteView.as_view(), name="conta_pagar_delete"),

    # Encargos de Conta a Pagar
    path("contas-pagar/<int:conta_pk>/encargos/novo/", views.EncargoContaPagarCreateView.as_view(), name="encargo_conta_pagar_create"),
    path("contas-pagar/encargos/<int:pk>/excluir/", views.EncargoContaPagarDeleteView.as_view(), name="encargo_conta_pagar_delete"),

    # Documentos de Conta a Pagar
    path("contas-pagar/<int:conta_pk>/documentos/novo/", views.DocumentoContaPagarCreateView.as_view(), name="documento_conta_pagar_create"),
    path("contas-pagar/documentos/<int:pk>/excluir/", views.DocumentoContaPagarDeleteView.as_view(), name="documento_conta_pagar_delete"),

    # Aprovação de Conta a Pagar
    path("contas-pagar/<int:conta_pk>/aprovacao/", views.AprovacaoContaPagarCreateView.as_view(), name="aprovacao_conta_pagar"),

    # ── Contas a Receber ─────────────────────
    path("contas-receber/", views.ContaReceberListView.as_view(), name="conta_receber_list"),
    path("contas-receber/nova/", views.ContaReceberCreateView.as_view(), name="conta_receber_create"),
    path("contas-receber/<int:pk>/", views.ContaReceberDetailView.as_view(), name="conta_receber_detail"),
    path("contas-receber/<int:pk>/editar/", views.ContaReceberUpdateView.as_view(), name="conta_receber_update"),
    path("contas-receber/<int:pk>/excluir/", views.ContaReceberDeleteView.as_view(), name="conta_receber_delete"),

    # Encargos de Conta a Receber
    path("contas-receber/<int:conta_pk>/encargos/novo/", views.EncargoContaReceberCreateView.as_view(), name="encargo_conta_receber_create"),
    path("contas-receber/encargos/<int:pk>/excluir/", views.EncargoContaReceberDeleteView.as_view(), name="encargo_conta_receber_delete"),

    # Documentos de Conta a Receber
    path("contas-receber/<int:conta_pk>/documentos/novo/", views.DocumentoContaReceberCreateView.as_view(), name="documento_conta_receber_create"),
    path("contas-receber/documentos/<int:pk>/excluir/", views.DocumentoContaReceberDeleteView.as_view(), name="documento_conta_receber_delete"),

    # ── Lançamentos ──────────────────────────
    path("lancamentos/", views.LancamentoFinanceiroListView.as_view(), name="lancamento_list"),
    path("lancamentos/novo/", views.LancamentoFinanceiroCreateView.as_view(), name="lancamento_create"),
    path("lancamentos/<int:pk>/editar/", views.LancamentoFinanceiroUpdateView.as_view(), name="lancamento_update"),
    path("lancamentos/<int:pk>/excluir/", views.LancamentoFinanceiroDeleteView.as_view(), name="lancamento_delete"),

    # ── Transferências Bancárias ─────────────
    path("transferencias/", views.TransferenciaBancariaListView.as_view(), name="transferencia_list"),
    path("transferencias/nova/", views.TransferenciaBancariaCreateView.as_view(), name="transferencia_create"),
    path("transferencias/<int:pk>/excluir/", views.TransferenciaBancariaDeleteView.as_view(), name="transferencia_delete"),

    # ── Projeção de Fluxo de Caixa ───────────
    path("projecoes/", views.ProjecaoFluxoCaixaListView.as_view(), name="projecao_list"),
    path("projecoes/nova/", views.ProjecaoFluxoCaixaCreateView.as_view(), name="projecao_create"),
    path("projecoes/<int:pk>/excluir/", views.ProjecaoFluxoCaixaDeleteView.as_view(), name="projecao_delete"),
]