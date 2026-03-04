from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from apps.authentication.mixins import PermissaoModuloMixin
from .models import (
    TipoPessoa, CategoriaFornecedor, CategoriaCliente,
    TipoConta, TipoChavePix, TipoPlanoContas, TipoCentroCusto,
    Fornecedor, ContatoFornecedor,
    Cliente, ContatoCliente,
    Banco, ContaBancaria,
    PlanoContas, CentroCusto,
)
from .forms import (
    FornecedorForm, ContatoFornecedorForm,
    ClienteForm, ContatoClienteForm,
    ContaBancariaForm,
    PlanoContasForm,
    CentroCustoForm,
    TipoPessoaForm, CategoriaFornecedorForm, CategoriaClienteForm,
    TipoContaForm, TipoChavePixForm, TipoPlanoContasForm, TipoCentroCustoForm, BancoForm,
)


# ══════════════════════════════════════════════
# MIXIN LOCAL
# ══════════════════════════════════════════════

class MensagemSucessoMixin:
    mensagem_criado    = "Registro criado com sucesso."
    mensagem_atualizado = "Registro atualizado com sucesso."
    mensagem_excluido  = "Registro excluído com sucesso."

    def form_valid(self, form):
        msg = self.mensagem_criado if not form.instance.pk else self.mensagem_atualizado
        messages.success(self.request, msg)
        return super().form_valid(form)

    def delete(self, request, *args, **kwargs):
        messages.success(request, self.mensagem_excluido)
        return super().delete(request, *args, **kwargs)


# ══════════════════════════════════════════════
# TABELAS DE DOMÍNIO — GLOBAIS
# ══════════════════════════════════════════════

class TipoPessoaListView(PermissaoModuloMixin, ListView):
    model = TipoPessoa
    template_name = "sistema/dominio_list.html"
    context_object_name = "objetos"
    modulo = "sistema"
    acao = "ver"
    extra_context = {
        "titulo": "Tipos de Pessoa",
        "create_url": "sistema:tipo_pessoa_create",
        "update_url": "sistema:tipo_pessoa_update",
        "delete_url": "sistema:tipo_pessoa_delete",
    }

    def get_queryset(self):
        return TipoPessoa.objects.all().order_by("nome")


class TipoPessoaCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = TipoPessoa
    form_class = TipoPessoaForm
    template_name = "sistema/dominio_form.html"
    success_url = reverse_lazy("sistema:tipo_pessoa_list")
    modulo = "sistema"
    acao = "criar"
    extra_context = {"titulo": "Novo Tipo de Pessoa", "list_url": "sistema:tipo_pessoa_list"}


class TipoPessoaUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = TipoPessoa
    form_class = TipoPessoaForm
    template_name = "sistema/dominio_form.html"
    success_url = reverse_lazy("sistema:tipo_pessoa_list")
    modulo = "sistema"
    acao = "editar"
    extra_context = {"titulo": "Editar Tipo de Pessoa", "list_url": "sistema:tipo_pessoa_list"}


class TipoPessoaDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = TipoPessoa
    template_name = "sistema/dominio_confirmar_exclusao.html"
    success_url = reverse_lazy("sistema:tipo_pessoa_list")
    modulo = "sistema"
    acao = "excluir"


# ── Categoria Fornecedor ─────────────────────

class CategoriaFornecedorListView(PermissaoModuloMixin, ListView):
    model = CategoriaFornecedor
    template_name = "sistema/dominio_list.html"
    context_object_name = "objetos"
    modulo = "sistema"
    acao = "ver"
    extra_context = {
        "titulo": "Categorias de Fornecedor",
        "create_url": "sistema:categoria_fornecedor_create",
        "update_url": "sistema:categoria_fornecedor_update",
        "delete_url": "sistema:categoria_fornecedor_delete",
    }

    def get_queryset(self):
        return CategoriaFornecedor.objects.filter(empresa=self.get_empresa()).order_by("nome")


class CategoriaFornecedorCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = CategoriaFornecedor
    form_class = CategoriaFornecedorForm
    template_name = "sistema/dominio_form.html"
    success_url = reverse_lazy("sistema:categoria_fornecedor_list")
    modulo = "sistema"
    acao = "criar"
    extra_context = {"titulo": "Nova Categoria de Fornecedor", "list_url": "sistema:categoria_fornecedor_list"}

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        return super().form_valid(form)


class CategoriaFornecedorUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = CategoriaFornecedor
    form_class = CategoriaFornecedorForm
    template_name = "sistema/dominio_form.html"
    success_url = reverse_lazy("sistema:categoria_fornecedor_list")
    modulo = "sistema"
    acao = "editar"
    extra_context = {"titulo": "Editar Categoria de Fornecedor", "list_url": "sistema:categoria_fornecedor_list"}

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw


class CategoriaFornecedorDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = CategoriaFornecedor
    template_name = "sistema/dominio_confirmar_exclusao.html"
    success_url = reverse_lazy("sistema:categoria_fornecedor_list")
    modulo = "sistema"
    acao = "excluir"


# ── Categoria Cliente ────────────────────────

class CategoriaClienteListView(PermissaoModuloMixin, ListView):
    model = CategoriaCliente
    template_name = "sistema/dominio_list.html"
    context_object_name = "objetos"
    modulo = "sistema"
    acao = "ver"
    extra_context = {
        "titulo": "Categorias de Cliente",
        "create_url": "sistema:categoria_cliente_create",
        "update_url": "sistema:categoria_cliente_update",
        "delete_url": "sistema:categoria_cliente_delete",
    }

    def get_queryset(self):
        return CategoriaCliente.objects.filter(empresa=self.get_empresa()).order_by("nome")


class CategoriaClienteCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = CategoriaCliente
    form_class = CategoriaClienteForm
    template_name = "sistema/dominio_form.html"
    success_url = reverse_lazy("sistema:categoria_cliente_list")
    modulo = "sistema"
    acao = "criar"
    extra_context = {"titulo": "Nova Categoria de Cliente", "list_url": "sistema:categoria_cliente_list"}

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        return super().form_valid(form)


class CategoriaClienteUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = CategoriaCliente
    form_class = CategoriaClienteForm
    template_name = "sistema/dominio_form.html"
    success_url = reverse_lazy("sistema:categoria_cliente_list")
    modulo = "sistema"
    acao = "editar"
    extra_context = {"titulo": "Editar Categoria de Cliente", "list_url": "sistema:categoria_cliente_list"}

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw


class CategoriaClienteDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = CategoriaCliente
    template_name = "sistema/dominio_confirmar_exclusao.html"
    success_url = reverse_lazy("sistema:categoria_cliente_list")
    modulo = "sistema"
    acao = "excluir"


# ── Tipo de Conta ────────────────────────────

class TipoContaListView(PermissaoModuloMixin, ListView):
    model = TipoConta
    template_name = "sistema/dominio_list.html"
    context_object_name = "objetos"
    modulo = "sistema"
    acao = "ver"
    extra_context = {
        "titulo": "Tipos de Conta Bancária",
        "create_url": "sistema:tipo_conta_create",
        "update_url": "sistema:tipo_conta_update",
        "delete_url": "sistema:tipo_conta_delete",
    }

    def get_queryset(self):
        return TipoConta.objects.all().order_by("nome")


class TipoContaCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = TipoConta
    form_class = TipoContaForm
    template_name = "sistema/dominio_form.html"
    success_url = reverse_lazy("sistema:tipo_conta_list")
    modulo = "sistema"
    acao = "criar"
    extra_context = {"titulo": "Novo Tipo de Conta", "list_url": "sistema:tipo_conta_list"}


class TipoContaUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = TipoConta
    form_class = TipoContaForm
    template_name = "sistema/dominio_form.html"
    success_url = reverse_lazy("sistema:tipo_conta_list")
    modulo = "sistema"
    acao = "editar"
    extra_context = {"titulo": "Editar Tipo de Conta", "list_url": "sistema:tipo_conta_list"}


class TipoContaDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = TipoConta
    template_name = "sistema/dominio_confirmar_exclusao.html"
    success_url = reverse_lazy("sistema:tipo_conta_list")
    modulo = "sistema"
    acao = "excluir"


# ── Tipo de Chave PIX ────────────────────────

class TipoChavePixListView(PermissaoModuloMixin, ListView):
    model = TipoChavePix
    template_name = "sistema/dominio_list.html"
    context_object_name = "objetos"
    modulo = "sistema"
    acao = "ver"
    extra_context = {
        "titulo": "Tipos de Chave PIX",
        "create_url": "sistema:tipo_chave_pix_create",
        "update_url": "sistema:tipo_chave_pix_update",
        "delete_url": "sistema:tipo_chave_pix_delete",
    }

    def get_queryset(self):
        return TipoChavePix.objects.all().order_by("nome")


class TipoChavePixCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = TipoChavePix
    form_class = TipoChavePixForm
    template_name = "sistema/dominio_form.html"
    success_url = reverse_lazy("sistema:tipo_chave_pix_list")
    modulo = "sistema"
    acao = "criar"
    extra_context = {"titulo": "Novo Tipo de Chave PIX", "list_url": "sistema:tipo_chave_pix_list"}


class TipoChavePixUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = TipoChavePix
    form_class = TipoChavePixForm
    template_name = "sistema/dominio_form.html"
    success_url = reverse_lazy("sistema:tipo_chave_pix_list")
    modulo = "sistema"
    acao = "editar"
    extra_context = {"titulo": "Editar Tipo de Chave PIX", "list_url": "sistema:tipo_chave_pix_list"}


class TipoChavePixDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = TipoChavePix
    template_name = "sistema/dominio_confirmar_exclusao.html"
    success_url = reverse_lazy("sistema:tipo_chave_pix_list")
    modulo = "sistema"
    acao = "excluir"


# ── Tipo de Plano de Contas ──────────────────

class TipoPlanoContasListView(PermissaoModuloMixin, ListView):
    model = TipoPlanoContas
    template_name = "sistema/dominio_list.html"
    context_object_name = "objetos"
    modulo = "sistema"
    acao = "ver"
    extra_context = {
        "titulo": "Tipos de Plano de Contas",
        "create_url": "sistema:tipo_plano_contas_create",
        "update_url": "sistema:tipo_plano_contas_update",
        "delete_url": "sistema:tipo_plano_contas_delete",
    }

    def get_queryset(self):
        return TipoPlanoContas.objects.all().order_by("nome")


class TipoPlanoContasCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = TipoPlanoContas
    form_class = TipoPlanoContasForm
    template_name = "sistema/dominio_form.html"
    success_url = reverse_lazy("sistema:tipo_plano_contas_list")
    modulo = "sistema"
    acao = "criar"
    extra_context = {"titulo": "Novo Tipo de Plano de Contas", "list_url": "sistema:tipo_plano_contas_list"}


class TipoPlanoContasUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = TipoPlanoContas
    form_class = TipoPlanoContasForm
    template_name = "sistema/dominio_form.html"
    success_url = reverse_lazy("sistema:tipo_plano_contas_list")
    modulo = "sistema"
    acao = "editar"
    extra_context = {"titulo": "Editar Tipo de Plano de Contas", "list_url": "sistema:tipo_plano_contas_list"}

    def get_queryset(self):
        return TipoPlanoContas.objects.all()


class TipoPlanoContasDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = TipoPlanoContas
    template_name = "sistema/dominio_confirmar_exclusao.html"
    success_url = reverse_lazy("sistema:tipo_plano_contas_list")
    modulo = "sistema"
    acao = "excluir"


# ── Tipo de Centro de Custo ──────────────────

class TipoCentroCustoListView(PermissaoModuloMixin, ListView):
    model = TipoCentroCusto
    template_name = "sistema/dominio_list.html"
    context_object_name = "objetos"
    modulo = "sistema"
    acao = "ver"
    extra_context = {
        "titulo": "Tipos de Centro de Custo",
        "create_url": "sistema:tipo_centro_custo_create",
        "update_url": "sistema:tipo_centro_custo_update",
        "delete_url": "sistema:tipo_centro_custo_delete",
    }

    def get_queryset(self):
        return TipoCentroCusto.objects.all().order_by("nome")


class TipoCentroCustoCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = TipoCentroCusto
    form_class = TipoCentroCustoForm
    template_name = "sistema/dominio_form.html"
    success_url = reverse_lazy("sistema:tipo_centro_custo_list")
    modulo = "sistema"
    acao = "criar"
    extra_context = {"titulo": "Novo Tipo de Centro de Custo", "list_url": "sistema:tipo_centro_custo_list"}


class TipoCentroCustoUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = TipoCentroCusto
    form_class = TipoCentroCustoForm
    template_name = "sistema/dominio_form.html"
    success_url = reverse_lazy("sistema:tipo_centro_custo_list")
    modulo = "sistema"
    acao = "editar"
    extra_context = {"titulo": "Editar Tipo de Centro de Custo", "list_url": "sistema:tipo_centro_custo_list"}

    def get_queryset(self):
        return TipoCentroCusto.objects.all()


class TipoCentroCustoDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = TipoCentroCusto
    template_name = "sistema/dominio_confirmar_exclusao.html"
    success_url = reverse_lazy("sistema:tipo_centro_custo_list")
    modulo = "sistema"
    acao = "excluir"

    def get_queryset(self):
        return TipoCentroCusto.objects.all()


# ══════════════════════════════════════════════
# FORNECEDORES
# ══════════════════════════════════════════════

class FornecedorListView(PermissaoModuloMixin, ListView):
    model = Fornecedor
    template_name = "sistema/fornecedor_list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "sistema"
    acao = "ver"

    def get_queryset(self):
        qs = super().get_queryset().select_related("tipo_pessoa", "categoria")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(razao_social__icontains=q) | qs.filter(cpf_cnpj__icontains=q)
        categoria = self.request.GET.get("categoria")
        if categoria:
            qs = qs.filter(categoria_id=categoria)
        ativo = self.request.GET.get("ativo")
        if ativo in ("true", "false"):
            qs = qs.filter(ativo=(ativo == "true"))
        return qs.order_by("razao_social")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categorias"] = CategoriaFornecedor.objects.filter(empresa=self.get_empresa(), ativo=True)
        return ctx


class FornecedorCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = Fornecedor
    form_class = FornecedorForm
    template_name = "sistema/fornecedor_form.html"
    modulo = "sistema"
    acao = "criar"
    extra_context = {"titulo": "Novo Fornecedor"}

    def get_success_url(self):
        return reverse_lazy("sistema:fornecedor_detail", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        return super().form_valid(form)


class FornecedorDetailView(PermissaoModuloMixin, DetailView):
    model = Fornecedor
    template_name = "sistema/fornecedor_detail.html"
    context_object_name = "fornecedor"
    modulo = "sistema"
    acao = "ver"

    def get_queryset(self):
        return Fornecedor.objects.filter(empresa=self.get_empresa())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["contatos"] = self.object.contatos.select_related("tipo").order_by("-principal", "tipo__nome")
        return ctx


class FornecedorUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = Fornecedor
    form_class = FornecedorForm
    template_name = "sistema/fornecedor_form.html"
    modulo = "sistema"
    acao = "editar"
    extra_context = {"titulo": "Editar Fornecedor"}

    def get_success_url(self):
        return reverse_lazy("sistema:fornecedor_detail", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw


class FornecedorDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = Fornecedor
    template_name = "sistema/fornecedor_confirmar_exclusao.html"
    success_url = reverse_lazy("sistema:fornecedor_list")
    modulo = "sistema"
    acao = "excluir"


# ── Contatos do Fornecedor ───────────────────

class ContatoFornecedorCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = ContatoFornecedor
    form_class = ContatoFornecedorForm
    template_name = "sistema/fornecedor_contato_form.html"
    modulo = "sistema"
    acao = "editar"

    def get_success_url(self):
        return reverse_lazy("sistema:fornecedor_detail", kwargs={"pk": self.kwargs["fornecedor_pk"]})

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def form_valid(self, form):
        form.instance.fornecedor = Fornecedor.objects.get(
            pk=self.kwargs["fornecedor_pk"], empresa=self.get_empresa()
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["fornecedor"] = Fornecedor.objects.get(pk=self.kwargs["fornecedor_pk"])
        return ctx


class ContatoFornecedorDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = ContatoFornecedor
    template_name = "sistema/fornecedor_confirmar_exclusao_contato.html"
    modulo = "sistema"
    acao = "editar"

    def get_success_url(self):
        return reverse_lazy("sistema:fornecedor_detail", kwargs={"pk": self.object.fornecedor_id})

    def get_queryset(self):
        return ContatoFornecedor.objects.filter(fornecedor__empresa=self.get_empresa())


# ══════════════════════════════════════════════
# CLIENTES
# ══════════════════════════════════════════════

class ClienteListView(PermissaoModuloMixin, ListView):
    model = Cliente
    template_name = "sistema/cliente_list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "sistema"
    acao = "ver"

    def get_queryset(self):
        qs = super().get_queryset().select_related("tipo_pessoa", "categoria")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(razao_social__icontains=q) | qs.filter(cpf_cnpj__icontains=q)
        categoria = self.request.GET.get("categoria")
        if categoria:
            qs = qs.filter(categoria_id=categoria)
        inadimplente = self.request.GET.get("inadimplente")
        if inadimplente in ("true", "false"):
            qs = qs.filter(inadimplente=(inadimplente == "true"))
        ativo = self.request.GET.get("ativo")
        if ativo in ("true", "false"):
            qs = qs.filter(ativo=(ativo == "true"))
        return qs.order_by("razao_social")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categorias"] = CategoriaCliente.objects.filter(empresa=self.get_empresa(), ativo=True)
        return ctx


class ClienteCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "sistema/cliente_form.html"
    modulo = "sistema"
    acao = "criar"
    extra_context = {"titulo": "Novo Cliente"}

    def get_success_url(self):
        return reverse_lazy("sistema:cliente_detail", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        return super().form_valid(form)


class ClienteDetailView(PermissaoModuloMixin, DetailView):
    model = Cliente
    template_name = "sistema/cliente_detail.html"
    context_object_name = "cliente"
    modulo = "sistema"
    acao = "ver"

    def get_queryset(self):
        return Cliente.objects.filter(empresa=self.get_empresa())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["contatos"] = self.object.contatos.select_related("tipo").order_by("-principal", "tipo__nome")
        return ctx


class ClienteUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "sistema/cliente_form.html"
    modulo = "sistema"
    acao = "editar"
    extra_context = {"titulo": "Editar Cliente"}

    def get_success_url(self):
        return reverse_lazy("sistema:cliente_detail", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw


class ClienteDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = Cliente
    template_name = "sistema/cliente_confirmar_exclusao.html"
    success_url = reverse_lazy("sistema:cliente_list")
    modulo = "sistema"
    acao = "excluir"


# ── Contatos do Cliente ──────────────────────

class ContatoClienteCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = ContatoCliente
    form_class = ContatoClienteForm
    template_name = "sistema/cliente_contato_form.html"
    modulo = "sistema"
    acao = "editar"

    def get_success_url(self):
        return reverse_lazy("sistema:cliente_detail", kwargs={"pk": self.kwargs["cliente_pk"]})

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def form_valid(self, form):
        form.instance.cliente = Cliente.objects.get(
            pk=self.kwargs["cliente_pk"], empresa=self.get_empresa()
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["cliente"] = Cliente.objects.get(pk=self.kwargs["cliente_pk"])
        return ctx


class ContatoClienteDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = ContatoCliente
    template_name = "sistema/cliente_confirmar_exclusao_contato.html"
    modulo = "sistema"
    acao = "editar"

    def get_success_url(self):
        return reverse_lazy("sistema:cliente_detail", kwargs={"pk": self.object.cliente_id})

    def get_queryset(self):
        return ContatoCliente.objects.filter(cliente__empresa=self.get_empresa())


# ══════════════════════════════════════════════
# BANCOS
# ══════════════════════════════════════════════

class BancoListView(PermissaoModuloMixin, ListView):
    model = Banco
    template_name = "sistema/banco_list.html"
    context_object_name = "objetos"
    paginate_by = 50
    modulo = "sistema"
    acao = "ver"

    def get_queryset(self):
        qs = Banco.objects.all().order_by("codigo")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(nome__icontains=q) | qs.filter(codigo__icontains=q)
        return qs


class BancoCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = Banco
    form_class = BancoForm
    template_name = "sistema/banco_form.html"
    success_url = reverse_lazy("sistema:banco_list")
    modulo = "sistema"
    acao = "criar"
    extra_context = {"titulo": "Novo Banco"}


class BancoUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = Banco
    form_class = BancoForm
    template_name = "sistema/banco_form.html"
    success_url = reverse_lazy("sistema:banco_list")
    modulo = "sistema"
    acao = "editar"
    extra_context = {"titulo": "Editar Banco"}

    def get_queryset(self):
        return Banco.objects.all()


class BancoDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = Banco
    template_name = "sistema/dominio_confirmar_exclusao.html"
    success_url = reverse_lazy("sistema:banco_list")
    modulo = "sistema"
    acao = "excluir"

    def get_queryset(self):
        return Banco.objects.all()


# ══════════════════════════════════════════════
# CONTAS BANCÁRIAS
# ══════════════════════════════════════════════

class ContaBancariaListView(PermissaoModuloMixin, ListView):
    model = ContaBancaria
    template_name = "sistema/conta_bancaria_list.html"
    context_object_name = "objetos"
    modulo = "sistema"
    acao = "ver"

    def get_queryset(self):
        return (
            super().get_queryset()
            .select_related("banco", "tipo_conta", "filial")
            .order_by("nome")
        )


class ContaBancariaCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = ContaBancaria
    form_class = ContaBancariaForm
    template_name = "sistema/conta_bancaria_form.html"
    success_url = reverse_lazy("sistema:conta_bancaria_list")
    modulo = "sistema"
    acao = "criar"
    extra_context = {"titulo": "Nova Conta Bancária"}

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        return super().form_valid(form)


class ContaBancariaUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = ContaBancaria
    form_class = ContaBancariaForm
    template_name = "sistema/conta_bancaria_form.html"
    success_url = reverse_lazy("sistema:conta_bancaria_list")
    modulo = "sistema"
    acao = "editar"
    extra_context = {"titulo": "Editar Conta Bancária"}

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw


class ContaBancariaDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = ContaBancaria
    template_name = "sistema/conta_bancaria_confirmar_exclusao.html"
    success_url = reverse_lazy("sistema:conta_bancaria_list")
    modulo = "sistema"
    acao = "excluir"


# ══════════════════════════════════════════════
# PLANO DE CONTAS
# ══════════════════════════════════════════════

class PlanoContasListView(PermissaoModuloMixin, ListView):
    model = PlanoContas
    template_name = "sistema/plano_contas_list.html"
    context_object_name = "objetos"
    modulo = "sistema"
    acao = "ver"

    def get_queryset(self):
        qs = super().get_queryset().select_related("tipo", "conta_pai")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(nome__icontains=q) | qs.filter(codigo__icontains=q)
        tipo = self.request.GET.get("tipo")
        if tipo:
            qs = qs.filter(tipo_id=tipo)
        analitica = self.request.GET.get("analitica")
        if analitica in ("true", "false"):
            qs = qs.filter(analitica=(analitica == "true"))
        return qs.order_by("codigo")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tipos"] = TipoPlanoContas.objects.filter(ativo=True)
        return ctx


class PlanoContasCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = PlanoContas
    form_class = PlanoContasForm
    template_name = "sistema/plano_contas_form.html"
    success_url = reverse_lazy("sistema:plano_contas_list")
    modulo = "sistema"
    acao = "criar"
    extra_context = {"titulo": "Nova Conta Contábil"}

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        return super().form_valid(form)


class PlanoContasUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = PlanoContas
    form_class = PlanoContasForm
    template_name = "sistema/plano_contas_form.html"
    success_url = reverse_lazy("sistema:plano_contas_list")
    modulo = "sistema"
    acao = "editar"
    extra_context = {"titulo": "Editar Conta Contábil"}

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw


class PlanoContasDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = PlanoContas
    template_name = "sistema/plano_contas_confirmar_exclusao.html"
    success_url = reverse_lazy("sistema:plano_contas_list")
    modulo = "sistema"
    acao = "excluir"


# ══════════════════════════════════════════════
# CENTRO DE CUSTO
# ══════════════════════════════════════════════

class CentroCustoListView(PermissaoModuloMixin, ListView):
    model = CentroCusto
    template_name = "sistema/centro_custo_list.html"
    context_object_name = "objetos"
    modulo = "sistema"
    acao = "ver"

    def get_queryset(self):
        qs = super().get_queryset().select_related("tipo")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(nome__icontains=q) | qs.filter(codigo__icontains=q)
        return qs.order_by("codigo")


class CentroCustoCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = CentroCusto
    form_class = CentroCustoForm
    template_name = "sistema/centro_custo_form.html"
    success_url = reverse_lazy("sistema:centro_custo_list")
    modulo = "sistema"
    acao = "criar"
    extra_context = {"titulo": "Novo Centro de Custo"}

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        return super().form_valid(form)


class CentroCustoUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = CentroCusto
    form_class = CentroCustoForm
    template_name = "sistema/centro_custo_form.html"
    success_url = reverse_lazy("sistema:centro_custo_list")
    modulo = "sistema"
    acao = "editar"
    extra_context = {"titulo": "Editar Centro de Custo"}

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw


class CentroCustoDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = CentroCusto
    template_name = "sistema/centro_custo_confirmar_exclusao.html"
    success_url = reverse_lazy("sistema:centro_custo_list")
    modulo = "sistema"
    acao = "excluir"