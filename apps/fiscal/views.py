from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from apps.authentication.mixins import PermissaoModuloMixin
from .models import (
    TipoImposto, TipoObrigacaoFiscal, StatusObrigacaoFiscal,
    ConfiguracaoImpostoEmpresa, LancamentoImposto, ObrigacaoFiscal,
)
from .forms import (
    TipoImpostoForm, TipoObrigacaoFiscalForm, StatusObrigacaoFiscalForm,
    ConfiguracaoImpostoEmpresaForm, LancamentoImpostoForm, ObrigacaoFiscalForm,
)


# ══════════════════════════════════════════════
# MIXIN LOCAL
# ══════════════════════════════════════════════

class MensagemSucessoMixin:
    mensagem_criado     = "Registro criado com sucesso."
    mensagem_atualizado = "Registro atualizado com sucesso."
    mensagem_excluido   = "Registro excluído com sucesso."

    def form_valid(self, form):
        msg = self.mensagem_criado if not form.instance.pk else self.mensagem_atualizado
        messages.success(self.request, msg)
        return super().form_valid(form)

    def delete(self, request, *args, **kwargs):
        messages.success(request, self.mensagem_excluido)
        return super().delete(request, *args, **kwargs)


# ══════════════════════════════════════════════
# TABELAS DE DOMÍNIO
# ══════════════════════════════════════════════

class TipoImpostoListView(PermissaoModuloMixin, ListView):
    model = TipoImposto
    template_name = "fiscal/dominio_list.html"
    context_object_name = "objetos"
    modulo = "fiscal"
    acao = "ver"
    extra_context = {
        "titulo": "Tipos de Imposto",
        "create_url": "fiscal:tipo_imposto_create",
        "update_url": "fiscal:tipo_imposto_update",
        "delete_url": "fiscal:tipo_imposto_delete",
        "colunas_extras": ["Sigla", "Esfera"],
    }

    def get_queryset(self):
        return TipoImposto.objects.all().order_by("sigla")


class TipoImpostoCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = TipoImposto
    form_class = TipoImpostoForm
    template_name = "fiscal/dominio_form.html"
    success_url = reverse_lazy("fiscal:tipo_imposto_list")
    modulo = "fiscal"
    acao = "criar"
    extra_context = {"titulo": "Novo Tipo de Imposto", "list_url": "fiscal:tipo_imposto_list"}


class TipoImpostoUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = TipoImposto
    form_class = TipoImpostoForm
    template_name = "fiscal/dominio_form.html"
    success_url = reverse_lazy("fiscal:tipo_imposto_list")
    modulo = "fiscal"
    acao = "editar"
    extra_context = {"titulo": "Editar Tipo de Imposto", "list_url": "fiscal:tipo_imposto_list"}

    def get_queryset(self):
        return TipoImposto.objects.all()


class TipoImpostoDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = TipoImposto
    template_name = "fiscal/dominio_confirmar_exclusao.html"
    success_url = reverse_lazy("fiscal:tipo_imposto_list")
    modulo = "fiscal"
    acao = "excluir"

    def get_queryset(self):
        return TipoImposto.objects.all()


class TipoObrigacaoFiscalListView(PermissaoModuloMixin, ListView):
    model = TipoObrigacaoFiscal
    template_name = "fiscal/dominio_list.html"
    context_object_name = "objetos"
    modulo = "fiscal"
    acao = "ver"
    extra_context = {
        "titulo": "Tipos de Obrigação Fiscal",
        "create_url": "fiscal:tipo_obrigacao_create",
        "update_url": "fiscal:tipo_obrigacao_update",
        "delete_url": "fiscal:tipo_obrigacao_delete",
        "colunas_extras": ["Sigla", "Periodicidade"],
    }

    def get_queryset(self):
        return TipoObrigacaoFiscal.objects.all().order_by("nome")


class TipoObrigacaoFiscalCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = TipoObrigacaoFiscal
    form_class = TipoObrigacaoFiscalForm
    template_name = "fiscal/dominio_form.html"
    success_url = reverse_lazy("fiscal:tipo_obrigacao_list")
    modulo = "fiscal"
    acao = "criar"
    extra_context = {"titulo": "Novo Tipo de Obrigação Fiscal", "list_url": "fiscal:tipo_obrigacao_list"}


class TipoObrigacaoFiscalUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = TipoObrigacaoFiscal
    form_class = TipoObrigacaoFiscalForm
    template_name = "fiscal/dominio_form.html"
    success_url = reverse_lazy("fiscal:tipo_obrigacao_list")
    modulo = "fiscal"
    acao = "editar"
    extra_context = {"titulo": "Editar Tipo de Obrigação Fiscal", "list_url": "fiscal:tipo_obrigacao_list"}

    def get_queryset(self):
        return TipoObrigacaoFiscal.objects.all()


class TipoObrigacaoFiscalDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = TipoObrigacaoFiscal
    template_name = "fiscal/dominio_confirmar_exclusao.html"
    success_url = reverse_lazy("fiscal:tipo_obrigacao_list")
    modulo = "fiscal"
    acao = "excluir"

    def get_queryset(self):
        return TipoObrigacaoFiscal.objects.all()


class StatusObrigacaoFiscalListView(PermissaoModuloMixin, ListView):
    model = StatusObrigacaoFiscal
    template_name = "fiscal/dominio_list.html"
    context_object_name = "objetos"
    modulo = "fiscal"
    acao = "ver"
    extra_context = {
        "titulo": "Status de Obrigação Fiscal",
        "create_url": "fiscal:status_obrigacao_create",
        "update_url": "fiscal:status_obrigacao_update",
        "delete_url": "fiscal:status_obrigacao_delete",
    }

    def get_queryset(self):
        return StatusObrigacaoFiscal.objects.all().order_by("nome")


class StatusObrigacaoFiscalCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = StatusObrigacaoFiscal
    form_class = StatusObrigacaoFiscalForm
    template_name = "fiscal/dominio_form.html"
    success_url = reverse_lazy("fiscal:status_obrigacao_list")
    modulo = "fiscal"
    acao = "criar"
    extra_context = {"titulo": "Novo Status de Obrigação Fiscal", "list_url": "fiscal:status_obrigacao_list"}


class StatusObrigacaoFiscalUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = StatusObrigacaoFiscal
    form_class = StatusObrigacaoFiscalForm
    template_name = "fiscal/dominio_form.html"
    success_url = reverse_lazy("fiscal:status_obrigacao_list")
    modulo = "fiscal"
    acao = "editar"
    extra_context = {"titulo": "Editar Status de Obrigação Fiscal", "list_url": "fiscal:status_obrigacao_list"}

    def get_queryset(self):
        return StatusObrigacaoFiscal.objects.all()


class StatusObrigacaoFiscalDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = StatusObrigacaoFiscal
    template_name = "fiscal/dominio_confirmar_exclusao.html"
    success_url = reverse_lazy("fiscal:status_obrigacao_list")
    modulo = "fiscal"
    acao = "excluir"

    def get_queryset(self):
        return StatusObrigacaoFiscal.objects.all()


# ══════════════════════════════════════════════
# CONFIGURAÇÃO DE IMPOSTOS
# ══════════════════════════════════════════════

class ConfiguracaoImpostoListView(PermissaoModuloMixin, ListView):
    model = ConfiguracaoImpostoEmpresa
    template_name = "fiscal/configuracao_imposto_list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "fiscal"
    acao = "ver"

    def get_queryset(self):
        return (
            super().get_queryset()
            .select_related("tipo_imposto", "plano_contas_debito", "plano_contas_credito")
            .filter(empresa=self.get_empresa())
            .order_by("tipo_imposto__sigla", "-vigencia_inicio")
        )


class ConfiguracaoImpostoCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = ConfiguracaoImpostoEmpresa
    form_class = ConfiguracaoImpostoEmpresaForm
    template_name = "fiscal/configuracao_imposto_form.html"
    success_url = reverse_lazy("fiscal:configuracao_imposto_list")
    modulo = "fiscal"
    acao = "criar"
    extra_context = {"titulo": "Nova Configuração de Imposto"}

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        return super().form_valid(form)


class ConfiguracaoImpostoUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = ConfiguracaoImpostoEmpresa
    form_class = ConfiguracaoImpostoEmpresaForm
    template_name = "fiscal/configuracao_imposto_form.html"
    success_url = reverse_lazy("fiscal:configuracao_imposto_list")
    modulo = "fiscal"
    acao = "editar"
    extra_context = {"titulo": "Editar Configuração de Imposto"}

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def get_queryset(self):
        return ConfiguracaoImpostoEmpresa.objects.filter(empresa=self.get_empresa())


class ConfiguracaoImpostoDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = ConfiguracaoImpostoEmpresa
    template_name = "fiscal/configuracao_imposto_confirmar_exclusao.html"
    success_url = reverse_lazy("fiscal:configuracao_imposto_list")
    modulo = "fiscal"
    acao = "excluir"

    def get_queryset(self):
        return ConfiguracaoImpostoEmpresa.objects.filter(empresa=self.get_empresa())


# ══════════════════════════════════════════════
# LANÇAMENTOS DE IMPOSTOS
# ══════════════════════════════════════════════

class LancamentoImpostoListView(PermissaoModuloMixin, ListView):
    model = LancamentoImposto
    template_name = "fiscal/lancamento_imposto_list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "fiscal"
    acao = "ver"

    def get_queryset(self):
        qs = (
            super().get_queryset()
            .select_related("tipo_imposto", "configuracao")
            .filter(empresa=self.get_empresa())
            .order_by("data_vencimento")
        )
        if tipo_id := self.request.GET.get("tipo_imposto"):
            qs = qs.filter(tipo_imposto_id=tipo_id)
        if venc_de := self.request.GET.get("vencimento_de"):
            qs = qs.filter(data_vencimento__gte=venc_de)
        if venc_ate := self.request.GET.get("vencimento_ate"):
            qs = qs.filter(data_vencimento__lte=venc_ate)
        if pago := self.request.GET.get("pago"):
            if pago == "true":
                qs = qs.filter(valor_pago__gt=0)
            elif pago == "false":
                qs = qs.filter(valor_pago=0)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tipos_imposto"] = TipoImposto.objects.filter(ativo=True).order_by("sigla")
        ctx["hoje"] = timezone.now().date()
        return ctx


class LancamentoImpostoCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = LancamentoImposto
    form_class = LancamentoImpostoForm
    template_name = "fiscal/lancamento_imposto_form.html"
    success_url = reverse_lazy("fiscal:lancamento_imposto_list")
    modulo = "fiscal"
    acao = "criar"
    extra_context = {"titulo": "Novo Lançamento de Imposto"}

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        return super().form_valid(form)


class LancamentoImpostoUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = LancamentoImposto
    form_class = LancamentoImpostoForm
    template_name = "fiscal/lancamento_imposto_form.html"
    success_url = reverse_lazy("fiscal:lancamento_imposto_list")
    modulo = "fiscal"
    acao = "editar"
    extra_context = {"titulo": "Editar Lançamento de Imposto"}

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def get_queryset(self):
        return LancamentoImposto.objects.filter(empresa=self.get_empresa())


class LancamentoImpostoDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = LancamentoImposto
    template_name = "fiscal/lancamento_imposto_confirmar_exclusao.html"
    success_url = reverse_lazy("fiscal:lancamento_imposto_list")
    modulo = "fiscal"
    acao = "excluir"

    def get_queryset(self):
        return LancamentoImposto.objects.filter(empresa=self.get_empresa())


# ══════════════════════════════════════════════
# OBRIGAÇÕES FISCAIS
# ══════════════════════════════════════════════

class ObrigacaoFiscalListView(PermissaoModuloMixin, ListView):
    model = ObrigacaoFiscal
    template_name = "fiscal/obrigacao_list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "fiscal"
    acao = "ver"

    def get_queryset(self):
        qs = (
            super().get_queryset()
            .select_related("tipo", "status", "responsavel")
            .filter(empresa=self.get_empresa())
            .order_by("data_vencimento")
        )
        if status_id := self.request.GET.get("status"):
            qs = qs.filter(status_id=status_id)
        if venc_de := self.request.GET.get("vencimento_de"):
            qs = qs.filter(data_vencimento__gte=venc_de)
        if venc_ate := self.request.GET.get("vencimento_ate"):
            qs = qs.filter(data_vencimento__lte=venc_ate)
        if tipo_id := self.request.GET.get("tipo"):
            qs = qs.filter(tipo_id=tipo_id)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_list"] = StatusObrigacaoFiscal.objects.filter(ativo=True)
        ctx["tipos_list"]  = TipoObrigacaoFiscal.objects.filter(ativo=True).order_by("nome")
        ctx["hoje"] = timezone.now().date()
        return ctx


class ObrigacaoFiscalDetailView(PermissaoModuloMixin, DetailView):
    model = ObrigacaoFiscal
    template_name = "fiscal/obrigacao_detail.html"
    context_object_name = "obrigacao"
    modulo = "fiscal"
    acao = "ver"

    def get_queryset(self):
        return ObrigacaoFiscal.objects.filter(
            empresa=self.get_empresa()
        ).select_related("tipo", "status", "responsavel")


class ObrigacaoFiscalCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = ObrigacaoFiscal
    form_class = ObrigacaoFiscalForm
    template_name = "fiscal/obrigacao_form.html"
    modulo = "fiscal"
    acao = "criar"
    extra_context = {"titulo": "Nova Obrigação Fiscal"}

    def get_success_url(self):
        return reverse_lazy("fiscal:obrigacao_detail", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        return super().form_valid(form)


class ObrigacaoFiscalUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = ObrigacaoFiscal
    form_class = ObrigacaoFiscalForm
    template_name = "fiscal/obrigacao_form.html"
    modulo = "fiscal"
    acao = "editar"
    extra_context = {"titulo": "Editar Obrigação Fiscal"}

    def get_success_url(self):
        return reverse_lazy("fiscal:obrigacao_detail", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def get_queryset(self):
        return ObrigacaoFiscal.objects.filter(empresa=self.get_empresa())


class ObrigacaoFiscalDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = ObrigacaoFiscal
    template_name = "fiscal/obrigacao_confirmar_exclusao.html"
    success_url = reverse_lazy("fiscal:obrigacao_list")
    modulo = "fiscal"
    acao = "excluir"

    def get_queryset(self):
        return ObrigacaoFiscal.objects.filter(empresa=self.get_empresa())