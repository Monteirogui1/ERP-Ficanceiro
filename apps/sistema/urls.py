from django.urls import path
from . import views

app_name = "sistema"

urlpatterns = [

    # ── Tabelas de Domínio ───────────────────

    # Tipo de Pessoa
    path("dominios/tipos-pessoa/", views.TipoPessoaListView.as_view(), name="tipo_pessoa_list"),
    path("dominios/tipos-pessoa/novo/", views.TipoPessoaCreateView.as_view(), name="tipo_pessoa_create"),
    path("dominios/tipos-pessoa/<int:pk>/editar/", views.TipoPessoaUpdateView.as_view(), name="tipo_pessoa_update"),
    path("dominios/tipos-pessoa/<int:pk>/excluir/", views.TipoPessoaDeleteView.as_view(), name="tipo_pessoa_delete"),

    # Categoria Fornecedor
    path("dominios/categorias-fornecedor/", views.CategoriaFornecedorListView.as_view(), name="categoria_fornecedor_list"),
    path("dominios/categorias-fornecedor/nova/", views.CategoriaFornecedorCreateView.as_view(), name="categoria_fornecedor_create"),
    path("dominios/categorias-fornecedor/<int:pk>/editar/", views.CategoriaFornecedorUpdateView.as_view(), name="categoria_fornecedor_update"),
    path("dominios/categorias-fornecedor/<int:pk>/excluir/", views.CategoriaFornecedorDeleteView.as_view(), name="categoria_fornecedor_delete"),

    # Categoria Cliente
    path("dominios/categorias-cliente/", views.CategoriaClienteListView.as_view(), name="categoria_cliente_list"),
    path("dominios/categorias-cliente/nova/", views.CategoriaClienteCreateView.as_view(), name="categoria_cliente_create"),
    path("dominios/categorias-cliente/<int:pk>/editar/", views.CategoriaClienteUpdateView.as_view(), name="categoria_cliente_update"),
    path("dominios/categorias-cliente/<int:pk>/excluir/", views.CategoriaClienteDeleteView.as_view(), name="categoria_cliente_delete"),

    # Tipo de Conta
    path("dominios/tipos-conta/", views.TipoContaListView.as_view(), name="tipo_conta_list"),
    path("dominios/tipos-conta/novo/", views.TipoContaCreateView.as_view(), name="tipo_conta_create"),
    path("dominios/tipos-conta/<int:pk>/editar/", views.TipoContaUpdateView.as_view(), name="tipo_conta_update"),
    path("dominios/tipos-conta/<int:pk>/excluir/", views.TipoContaDeleteView.as_view(), name="tipo_conta_delete"),

    # Tipo de Chave PIX
    path("dominios/tipos-chave-pix/", views.TipoChavePixListView.as_view(), name="tipo_chave_pix_list"),
    path("dominios/tipos-chave-pix/novo/", views.TipoChavePixCreateView.as_view(), name="tipo_chave_pix_create"),
    path("dominios/tipos-chave-pix/<int:pk>/editar/", views.TipoChavePixUpdateView.as_view(), name="tipo_chave_pix_update"),
    path("dominios/tipos-chave-pix/<int:pk>/excluir/", views.TipoChavePixDeleteView.as_view(), name="tipo_chave_pix_delete"),

    # Tipo de Plano de Contas
    path("dominios/tipos-plano-contas/", views.TipoPlanoContasListView.as_view(), name="tipo_plano_contas_list"),
    path("dominios/tipos-plano-contas/novo/", views.TipoPlanoContasCreateView.as_view(), name="tipo_plano_contas_create"),
    path("dominios/tipos-plano-contas/<int:pk>/editar/", views.TipoPlanoContasUpdateView.as_view(), name="tipo_plano_contas_update"),
    path("dominios/tipos-plano-contas/<int:pk>/excluir/", views.TipoPlanoContasDeleteView.as_view(), name="tipo_plano_contas_delete"),

    # Tipo de Centro de Custo
    path("dominios/tipos-centro-custo/", views.TipoCentroCustoListView.as_view(), name="tipo_centro_custo_list"),
    path("dominios/tipos-centro-custo/novo/", views.TipoCentroCustoCreateView.as_view(), name="tipo_centro_custo_create"),
    path("dominios/tipos-centro-custo/<int:pk>/editar/", views.TipoCentroCustoUpdateView.as_view(), name="tipo_centro_custo_update"),
    path("dominios/tipos-centro-custo/<int:pk>/excluir/", views.TipoCentroCustoDeleteView.as_view(), name="tipo_centro_custo_delete"),

    # ── Fornecedores ─────────────────────────
    path("fornecedores/", views.FornecedorListView.as_view(), name="fornecedor_list"),
    path("fornecedores/novo/", views.FornecedorCreateView.as_view(), name="fornecedor_create"),
    path("fornecedores/<int:pk>/", views.FornecedorDetailView.as_view(), name="fornecedor_detail"),
    path("fornecedores/<int:pk>/editar/", views.FornecedorUpdateView.as_view(), name="fornecedor_update"),
    path("fornecedores/<int:pk>/excluir/", views.FornecedorDeleteView.as_view(), name="fornecedor_delete"),

    # Contatos do Fornecedor
    path("fornecedores/<int:fornecedor_pk>/contatos/novo/", views.ContatoFornecedorCreateView.as_view(), name="contato_fornecedor_create"),
    path("fornecedores/contatos/<int:pk>/excluir/", views.ContatoFornecedorDeleteView.as_view(), name="contato_fornecedor_delete"),

    # ── Clientes ─────────────────────────────
    path("clientes/", views.ClienteListView.as_view(), name="cliente_list"),
    path("clientes/novo/", views.ClienteCreateView.as_view(), name="cliente_create"),
    path("clientes/<int:pk>/", views.ClienteDetailView.as_view(), name="cliente_detail"),
    path("clientes/<int:pk>/editar/", views.ClienteUpdateView.as_view(), name="cliente_update"),
    path("clientes/<int:pk>/excluir/", views.ClienteDeleteView.as_view(), name="cliente_delete"),

    # Contatos do Cliente
    path("clientes/<int:cliente_pk>/contatos/novo/", views.ContatoClienteCreateView.as_view(), name="contato_cliente_create"),
    path("clientes/contatos/<int:pk>/excluir/", views.ContatoClienteDeleteView.as_view(), name="contato_cliente_delete"),

    # ── Bancos ───────────────────────────────
    path("bancos/", views.BancoListView.as_view(), name="banco_list"),
    path("bancos/novo/", views.BancoCreateView.as_view(), name="banco_create"),
    path("bancos/<int:pk>/editar/", views.BancoUpdateView.as_view(), name="banco_update"),
    path("bancos/<int:pk>/excluir/", views.BancoDeleteView.as_view(), name="banco_delete"),




    # ── Contas Bancárias ─────────────────────
    path("contas-bancarias/", views.ContaBancariaListView.as_view(), name="conta_bancaria_list"),
    path("contas-bancarias/nova/", views.ContaBancariaCreateView.as_view(), name="conta_bancaria_create"),
    path("contas-bancarias/<int:pk>/editar/", views.ContaBancariaUpdateView.as_view(), name="conta_bancaria_update"),
    path("contas-bancarias/<int:pk>/excluir/", views.ContaBancariaDeleteView.as_view(), name="conta_bancaria_delete"),

    # ── Plano de Contas ──────────────────────
    path("plano-contas/", views.PlanoContasListView.as_view(), name="plano_contas_list"),
    path("plano-contas/novo/", views.PlanoContasCreateView.as_view(), name="plano_contas_create"),
    path("plano-contas/<int:pk>/editar/", views.PlanoContasUpdateView.as_view(), name="plano_contas_update"),
    path("plano-contas/<int:pk>/excluir/", views.PlanoContasDeleteView.as_view(), name="plano_contas_delete"),

    # ── Centro de Custo ──────────────────────
    path("centros-custo/", views.CentroCustoListView.as_view(), name="centro_custo_list"),
    path("centros-custo/novo/", views.CentroCustoCreateView.as_view(), name="centro_custo_create"),
    path("centros-custo/<int:pk>/editar/", views.CentroCustoUpdateView.as_view(), name="centro_custo_update"),
    path("centros-custo/<int:pk>/excluir/", views.CentroCustoDeleteView.as_view(), name="centro_custo_delete"),
]