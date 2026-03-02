from django.views.generic import ListView, CreateView, UpdateView, DeleteView
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
    TipoContaForm, TipoChavePixForm, TipoPlanoContasForm, TipoCentroCustoForm,
)


# ─────────────────────────────────────────────
# MIXIN DE MENSAGEM PADRÃO
# ─────────────────────────────────────────────

class MensagemSucessoMixin:
    mensagem_criado = "Registro criado com sucesso."
    mensagem_atualizado = "Registro atualizado com sucesso."
    mensagem_excluido = "Registro excluído com sucesso."

    def form_valid(self, form):
        msg = self.mensagem_criado if not form.instance.pk else self.mensagem_atualizado
        messages.success(self.request, msg)
        return super().form_valid(form)

    def delete(self, request, *args, **kwargs):
        messages.success(request, self.mensagem_excluido)
        return super().delete(request, *args, **kwargs)


# ══════════════════════════════════════════════
# TABELAS DE DOMÍNIO (CHOICES CADASTRÁVEIS)
# ══════════════════════════════════════════════

# ── Tipo de Pessoa ──────────────────────────

class TipoPessoaListView(PermissaoModuloMixin, ListView):
    model = TipoPessoa
    template_name = "sistema/dominio/tipo_pessoa_list.html"
    context_object_name = "objetos"
    modulo = "sistema"
    acao = "ver"

    def get_queryset(self):
        return TipoPessoa.objects.all()


class TipoPessoaCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = TipoPessoa
    form_class = TipoPessoaForm
    template_name = "sistema/dominio/form.html"
    success_url = reverse_lazy("sistema:tipo_pessoa_list")
    modulo = "sistema"
    acao = "criar"
    extra_context = {"titulo": "Novo Tipo de Pessoa"}


class TipoPessoaUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = TipoPessoa
    form_class = TipoPessoaForm
    template_name = "sistema/dominio/form.html"
    success_url = reverse_lazy("sistema:tipo_pessoa_list")
    modulo = "sistema"
    acao = "editar"
    extra_context = {"titulo": "Editar Tipo de Pessoa"}

    def get_queryset(self):
        return TipoPessoa.objects.all()


class TipoPessoaDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = TipoPessoa
    template_name = "sistema/dominio/confirmar_exclusao.html"
    success_url = reverse_lazy("sistema:tipo_pessoa_list")
    modulo = "sistema"
    acao = "excluir"

    def get_queryset(self):
        return TipoPessoa.objects.all()


# ── Categoria Fornecedor ─────────────────────

class CategoriaFornecedorListView(PermissaoModuloMixin, ListView):
    model = CategoriaFornecedor
    template_name = "sistema/dominio/categoria_fornecedor_list.html"
    context_object_name = "objetos"
    modulo = "sistema"
    acao = "ver"


class CategoriaFornecedorCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = CategoriaFornecedor
    form_class = CategoriaFornecedorForm
    template_name = "sistema/dominio/form.html"
    success_url = reverse_lazy("sistema:categoria_fornecedor_list")
    modulo = "sistema"
    acao = "criar"
    extra_context = {"titulo": "Nova Categoria de Fornecedor"}


class CategoriaFornecedorUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = CategoriaFornecedor
    form_class = CategoriaFornecedorForm
    template_name = "sistema/dominio/form.html"
    success_url = reverse_lazy("sistema:categoria_fornecedor_list")
    modulo = "sistema"
    acao = "editar"
    extra_context = {"titulo": "Editar Categoria de Fornecedor"}


class CategoriaFornecedorDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = CategoriaFornecedor
    template_name = "sistema/dominio/confirmar_exclusao.html"
    success_url = reverse_lazy("sistema:categoria_fornecedor_list")
    modulo = "sistema"
    acao = "excluir"


# ── Categoria Cliente ────────────────────────

class CategoriaClienteListView(PermissaoModuloMixin, ListView):
    model = CategoriaCliente
    template_name = "sistema/dominio/categoria_cliente_list.html"
    context_object_name = "objetos"
    modulo = "sistema"
    acao = "ver"


class CategoriaClienteCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = CategoriaCliente
    form_class = CategoriaClienteForm
    template_name = "sistema/dominio/form.html"
    success_url = reverse_lazy("sistema:categoria_cliente_list")
    modulo = "sistema"
    acao = "criar"
    extra_context = {"titulo": "Nova Categoria de Cliente"}


class CategoriaClienteUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = CategoriaCliente
    form_class = CategoriaClienteForm
    template_name = "sistema/dominio/form.html"
    success_url = reverse_lazy("sistema:categoria_cliente_list")
    modulo = "sistema"
    acao = "editar"
    extra_context = {"titulo": "Editar Categoria de Cliente"}


class CategoriaClienteDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = CategoriaCliente
    template_name = "sistema/dominio/confirmar_exclusao.html"
    success_url = reverse_lazy("sistema:categoria_cliente_list")
    modulo = "sistema"
    acao = "excluir"


# ── Tipo de Conta ────────────────────────────

class TipoContaListView(PermissaoModuloMixin, ListView):
    model = TipoConta
    template_name = "sistema/dominio/tipo_conta_list.html"
    context_object_name = "objetos"
    modulo = "sistema"
    acao = "ver"

    def get_queryset(self):
        return TipoConta.objects.all()


class TipoContaCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = TipoConta
    form_class = TipoContaForm
    template_name = "sistema/dominio/form.html"
    success_url = reverse_lazy("sistema:tipo_conta_list")
    modulo = "sistema"
    acao = "criar"
    extra_context = {"titulo": "Novo Tipo de Conta"}


class TipoContaUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = TipoConta
    form_class = TipoContaForm
    template_name = "sistema/dominio/form.html"
    success_url = reverse_lazy("sistema:tipo_conta_list")
    modulo = "sistema"
    acao = "editar"
    extra_context = {"titulo": "Editar Tipo de Conta"}

    def get_queryset(self):
        return TipoConta.objects.all()


class TipoContaDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = TipoConta
    template_name = "sistema/dominio/confirmar_exclusao.html"
    success_url = reverse_lazy("sistema:tipo_conta_list")
    modulo = "sistema"
    acao = "excluir"

    def get_queryset(self):
        return TipoConta.objects.all()


# ── Tipo de Chave PIX ────────────────────────

class TipoChavePixListView(PermissaoModuloMixin, ListView):
    model = TipoChavePix
    template_name = "sistema/dominio/tipo_chave_pix_list.html"
    context_object_name = "objetos"
    modulo = "sistema"
    acao = "ver"

    def get_queryset(self):
        return TipoChavePix.objects.all()


class TipoChavePixCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = TipoChavePix
    form_class = TipoChavePixForm
    template_name = "sistema/dominio/form.html"
    success_url = reverse_lazy("sistema:tipo_chave_pix_list")
    modulo = "sistema"
    acao = "criar"
    extra_context = {"titulo": "Novo Tipo de Chave PIX"}


class TipoChavePixUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = TipoChavePix
    form_class = TipoChavePixForm
    template_name = "sistema/dominio/form.html"
    success_url = reverse_lazy("sistema:tipo_chave_pix_list")
    modulo = "sistema"
    acao = "editar"
    extra_context = {"titulo": "Editar Tipo de Chave PIX"}

    def get_queryset(self):
        return TipoChavePix.objects.all()


class TipoChavePixDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = TipoChavePix
    template_name = "sistema/dominio/confirmar_exclusao.html"
    success_url = reverse_lazy("sistema:tipo_chave_pix_list")
    modulo = "sistema"
    acao = "excluir"

    def get_queryset(self):
        return TipoChavePix.objects.all()


# ── Tipo de Plano de Contas ──────────────────

class TipoPlanoContasListView(PermissaoModuloMixin, ListView):
    model = TipoPlanoContas
    template_name = "sistema/dominio/tipo_plano_contas_list.html"
    context_object_name = "objetos"
    modulo = "sistema"
    acao = "ver"

    def get_queryset(self):
        return TipoPlanoContas.objects.all()


class TipoPlanoContasCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = TipoPlanoContas
    form_class = TipoPlanoContasForm
    template_name = "sistema/dominio/form.html"
    success_url = reverse_lazy("sistema:tipo_plano_contas_list")
    modulo = "sistema"
    acao = "criar"
    extra_context = {"titulo": "Novo Tipo de Plano de Contas"}


class TipoPlanoContasUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = TipoPlanoContas
    form_class = TipoPlanoContasForm
    template_name = "sistema/dominio/form.html"
    success_url = reverse_lazy("sistema:tipo_plano_contas_list")
    modulo = "sistema"
    acao = "editar"
    extra_context = {"titulo": "Editar Tipo de Plano de Contas"}

    def get_queryset(self):
        return TipoPlanoContas.objects.all()


class TipoPlanoContasDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = TipoPlanoContas
    template_name = "sistema/dominio/confirmar_exclusao.html"
    success_url = reverse_lazy("sistema:tipo_plano_contas_list")
    modulo = "sistema"
    acao = "excluir"

    def get_queryset(self):
        return TipoPlanoContas.objects.all()


# ── Tipo de Centro de Custo ──────────────────

class TipoCentroCustoListView(PermissaoModuloMixin, ListView):
    model = TipoCentroCusto
    template_name = "sistema/dominio/tipo_centro_custo_list.html"
    context_object_name = "objetos"
    modulo = "sistema"
    acao = "ver"

    def get_queryset(self):
        return TipoCentroCusto.objects.all()


class TipoCentroCustoCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = TipoCentroCusto
    form_class = TipoCentroCustoForm
    template_name = "sistema/dominio/form.html"
    success_url = reverse_lazy("sistema:tipo_centro_custo_list")
    modulo = "sistema"
    acao = "criar"
    extra_context = {"titulo": "Novo Tipo de Centro de Custo"}


class TipoCentroCustoUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = TipoCentroCusto
    form_class = TipoCentroCustoForm
    template_name = "sistema/dominio/form.html"
    success_url = reverse_lazy("sistema:tipo_centro_custo_list")
    modulo = "sistema"
    acao = "editar"
    extra_context = {"titulo": "Editar Tipo de Centro de Custo"}

    def get_queryset(self):
        return TipoCentroCusto.objects.all()


class TipoCentroCustoDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = TipoCentroCusto
    template_name = "sistema/dominio/confirmar_exclusao.html"
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
    template_name = "sistema/fornecedor/list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "sistema"
    acao = "ver"

    def get_queryset(self):
        qs = super().get_queryset().select_related("tipo_pessoa", "categoria")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(razao_social__icontains=q)
        ativo = self.request.GET.get("ativo")
        if ativo in ("true", "false"):
            qs = qs.filter(ativo=ativo == "true")
        return qs


class FornecedorCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = Fornecedor
    form_class = FornecedorForm
    template_name = "sistema/fornecedor/form.html"
    success_url = reverse_lazy("sistema:fornecedor_list")
    modulo = "sistema"
    acao = "criar"
    extra_context = {"titulo": "Novo Fornecedor"}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class FornecedorUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = Fornecedor
    form_class = FornecedorForm
    template_name = "sistema/fornecedor/form.html"
    success_url = reverse_lazy("sistema:fornecedor_list")
    modulo = "sistema"
    acao = "editar"
    extra_context = {"titulo": "Editar Fornecedor"}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class FornecedorDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = Fornecedor
    template_name = "sistema/fornecedor/confirmar_exclusao.html"
    success_url = reverse_lazy("sistema:fornecedor_list")
    modulo = "sistema"
    acao = "excluir"


class FornecedorDetailView(PermissaoModuloMixin, ListView):
    """Lista contatos do fornecedor na tela de detalhe."""
    model = ContatoFornecedor
    template_name = "sistema/fornecedor/detail.html"
    context_object_name = "contatos"
    modulo = "sistema"
    acao = "ver"

    def get_queryset(self):
        return ContatoFornecedor.objects.filter(
            fornecedor_id=self.kwargs["pk"],
            fornecedor__empresa=self.get_empresa(),
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["fornecedor"] = Fornecedor.objects.get(
            pk=self.kwargs["pk"], empresa=self.get_empresa()
        )
        return ctx


class ContatoFornecedorCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = ContatoFornecedor
    form_class = ContatoFornecedorForm
    template_name = "sistema/fornecedor/contato_form.html"
    modulo = "sistema"
    acao = "editar"

    def get_success_url(self):
        return reverse_lazy("sistema:fornecedor_detail", kwargs={"pk": self.kwargs["fornecedor_pk"]})

    def form_valid(self, form):
        form.instance.fornecedor = Fornecedor.objects.get(
            pk=self.kwargs["fornecedor_pk"], empresa=self.get_empresa()
        )
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class ContatoFornecedorDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = ContatoFornecedor
    template_name = "sistema/fornecedor/confirmar_exclusao_contato.html"
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
    template_name = "sistema/cliente/list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "sistema"
    acao = "ver"

    def get_queryset(self):
        qs = super().get_queryset().select_related("tipo_pessoa", "categoria")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(razao_social__icontains=q)
        inadimplente = self.request.GET.get("inadimplente")
        if inadimplente in ("true", "false"):
            qs = qs.filter(inadimplente=inadimplente == "true")
        ativo = self.request.GET.get("ativo")
        if ativo in ("true", "false"):
            qs = qs.filter(ativo=ativo == "true")
        return qs


class ClienteCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "sistema/cliente/form.html"
    success_url = reverse_lazy("sistema:cliente_list")
    modulo = "sistema"
    acao = "criar"
    extra_context = {"titulo": "Novo Cliente"}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class ClienteUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "sistema/cliente/form.html"
    success_url = reverse_lazy("sistema:cliente_list")
    modulo = "sistema"
    acao = "editar"
    extra_context = {"titulo": "Editar Cliente"}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class ClienteDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = Cliente
    template_name = "sistema/cliente/confirmar_exclusao.html"
    success_url = reverse_lazy("sistema:cliente_list")
    modulo = "sistema"
    acao = "excluir"


class ClienteDetailView(PermissaoModuloMixin, ListView):
    model = ContatoCliente
    template_name = "sistema/cliente/detail.html"
    context_object_name = "contatos"
    modulo = "sistema"
    acao = "ver"

    def get_queryset(self):
        return ContatoCliente.objects.filter(
            cliente_id=self.kwargs["pk"],
            cliente__empresa=self.get_empresa(),
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["cliente"] = Cliente.objects.get(pk=self.kwargs["pk"], empresa=self.get_empresa())
        return ctx


class ContatoClienteCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = ContatoCliente
    form_class = ContatoClienteForm
    template_name = "sistema/cliente/contato_form.html"
    modulo = "sistema"
    acao = "editar"

    def get_success_url(self):
        return reverse_lazy("sistema:cliente_detail", kwargs={"pk": self.kwargs["cliente_pk"]})

    def form_valid(self, form):
        form.instance.cliente = Cliente.objects.get(
            pk=self.kwargs["cliente_pk"], empresa=self.get_empresa()
        )
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class ContatoClienteDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = ContatoCliente
    template_name = "sistema/cliente/confirmar_exclusao_contato.html"
    modulo = "sistema"
    acao = "editar"

    def get_success_url(self):
        return reverse_lazy("sistema:cliente_detail", kwargs={"pk": self.object.cliente_id})

    def get_queryset(self):
        return ContatoCliente.objects.filter(cliente__empresa=self.get_empresa())


# ══════════════════════════════════════════════
# BANCOS E CONTAS BANCÁRIAS
# ══════════════════════════════════════════════

class BancoListView(PermissaoModuloMixin, ListView):
    model = Banco
    template_name = "sistema/banco/list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "sistema"
    acao = "ver"

    def get_queryset(self):
        return Banco.objects.all()


class ContaBancariaListView(PermissaoModuloMixin, ListView):
    model = ContaBancaria
    template_name = "sistema/conta_bancaria/list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "sistema"
    acao = "ver"

    def get_queryset(self):
        return super().get_queryset().select_related("banco", "tipo_conta")


class ContaBancariaCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = ContaBancaria
    form_class = ContaBancariaForm
    template_name = "sistema/conta_bancaria/form.html"
    success_url = reverse_lazy("sistema:conta_bancaria_list")
    modulo = "sistema"
    acao = "criar"
    extra_context = {"titulo": "Nova Conta Bancária"}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class ContaBancariaUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = ContaBancaria
    form_class = ContaBancariaForm
    template_name = "sistema/conta_bancaria/form.html"
    success_url = reverse_lazy("sistema:conta_bancaria_list")
    modulo = "sistema"
    acao = "editar"
    extra_context = {"titulo": "Editar Conta Bancária"}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class ContaBancariaDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = ContaBancaria
    template_name = "sistema/conta_bancaria/confirmar_exclusao.html"
    success_url = reverse_lazy("sistema:conta_bancaria_list")
    modulo = "sistema"
    acao = "excluir"


# ══════════════════════════════════════════════
# PLANO DE CONTAS
# ══════════════════════════════════════════════

class PlanoContasListView(PermissaoModuloMixin, ListView):
    model = PlanoContas
    template_name = "sistema/plano_contas/list.html"
    context_object_name = "objetos"
    modulo = "sistema"
    acao = "ver"

    def get_queryset(self):
        return super().get_queryset().select_related("tipo", "conta_pai").filter(conta_pai=None)


class PlanoContasCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = PlanoContas
    form_class = PlanoContasForm
    template_name = "sistema/plano_contas/form.html"
    success_url = reverse_lazy("sistema:plano_contas_list")
    modulo = "sistema"
    acao = "criar"
    extra_context = {"titulo": "Nova Conta"}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class PlanoContasUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = PlanoContas
    form_class = PlanoContasForm
    template_name = "sistema/plano_contas/form.html"
    success_url = reverse_lazy("sistema:plano_contas_list")
    modulo = "sistema"
    acao = "editar"
    extra_context = {"titulo": "Editar Conta"}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class PlanoContasDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = PlanoContas
    template_name = "sistema/plano_contas/confirmar_exclusao.html"
    success_url = reverse_lazy("sistema:plano_contas_list")
    modulo = "sistema"
    acao = "excluir"


# ══════════════════════════════════════════════
# CENTRO DE CUSTO
# ══════════════════════════════════════════════

class CentroCustoListView(PermissaoModuloMixin, ListView):
    model = CentroCusto
    template_name = "sistema/centro_custo/list.html"
    context_object_name = "objetos"
    modulo = "sistema"
    acao = "ver"

    def get_queryset(self):
        return super().get_queryset().select_related("tipo", "centro_pai").filter(centro_pai=None)


class CentroCustoCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = CentroCusto
    form_class = CentroCustoForm
    template_name = "sistema/centro_custo/form.html"
    success_url = reverse_lazy("sistema:centro_custo_list")
    modulo = "sistema"
    acao = "criar"
    extra_context = {"titulo": "Novo Centro de Custo"}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class CentroCustoUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = CentroCusto
    form_class = CentroCustoForm
    template_name = "sistema/centro_custo/form.html"
    success_url = reverse_lazy("sistema:centro_custo_list")
    modulo = "sistema"
    acao = "editar"
    extra_context = {"titulo": "Editar Centro de Custo"}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class CentroCustoDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = CentroCusto
    template_name = "sistema/centro_custo/confirmar_exclusao.html"
    success_url = reverse_lazy("sistema:centro_custo_list")
    modulo = "sistema"
    acao = "excluir"