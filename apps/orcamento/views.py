from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from apps.authentication.mixins import PermissaoModuloMixin
from .models import StatusOrcamento, Orcamento, ItemOrcamento, AlertaEstouroOrcamento
from .forms import StatusOrcamentoForm, OrcamentoForm, ItemOrcamentoForm


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


# ── Tabelas de Domínio ───────────────────────

class StatusOrcamentoListView(PermissaoModuloMixin, ListView):
    model = StatusOrcamento
    template_name = "orcamento/dominio/status_list.html"
    context_object_name = "objetos"
    modulo = "orcamento"
    acao = "ver"

    def get_queryset(self):
        return StatusOrcamento.objects.all()


class StatusOrcamentoCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = StatusOrcamento
    form_class = StatusOrcamentoForm
    template_name = "orcamento/dominio/form.html"
    success_url = reverse_lazy("orcamento:status_list")
    modulo = "orcamento"
    acao = "criar"
    extra_context = {"titulo": "Novo Status de Orçamento"}


class StatusOrcamentoUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = StatusOrcamento
    form_class = StatusOrcamentoForm
    template_name = "orcamento/dominio/form.html"
    success_url = reverse_lazy("orcamento:status_list")
    modulo = "orcamento"
    acao = "editar"
    extra_context = {"titulo": "Editar Status de Orçamento"}

    def get_queryset(self):
        return StatusOrcamento.objects.all()


class StatusOrcamentoDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = StatusOrcamento
    template_name = "orcamento/dominio/confirmar_exclusao.html"
    success_url = reverse_lazy("orcamento:status_list")
    modulo = "orcamento"
    acao = "excluir"

    def get_queryset(self):
        return StatusOrcamento.objects.all()


# ── Orçamentos ───────────────────────────────

class OrcamentoListView(PermissaoModuloMixin, ListView):
    model = Orcamento
    template_name = "orcamento/orcamento/list.html"
    context_object_name = "objetos"
    paginate_by = 20
    modulo = "orcamento"
    acao = "ver"

    def get_queryset(self):
        qs = super().get_queryset().select_related("status")
        ano = self.request.GET.get("ano")
        if ano:
            qs = qs.filter(ano=ano)
        status_id = self.request.GET.get("status")
        if status_id:
            qs = qs.filter(status_id=status_id)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_list"] = StatusOrcamento.objects.filter(ativo=True)
        return ctx


class OrcamentoDetailView(PermissaoModuloMixin, DetailView):
    model = Orcamento
    template_name = "orcamento/orcamento/detail.html"
    context_object_name = "orcamento"
    modulo = "orcamento"
    acao = "ver"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["itens"] = self.object.itens.select_related(
            "plano_contas", "centro_custo"
        ).order_by("mes", "plano_contas__codigo")
        ctx["alertas"] = AlertaEstouroOrcamento.objects.filter(
            item_orcamento__orcamento=self.object
        ).order_by("-criado_em")
        return ctx


class OrcamentoCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = Orcamento
    form_class = OrcamentoForm
    template_name = "orcamento/orcamento/form.html"
    success_url = reverse_lazy("orcamento:orcamento_list")
    modulo = "orcamento"
    acao = "criar"
    extra_context = {"titulo": "Novo Orçamento"}

    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class OrcamentoUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = Orcamento
    form_class = OrcamentoForm
    template_name = "orcamento/orcamento/form.html"
    success_url = reverse_lazy("orcamento:orcamento_list")
    modulo = "orcamento"
    acao = "editar"
    extra_context = {"titulo": "Editar Orçamento"}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class OrcamentoDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = Orcamento
    template_name = "orcamento/orcamento/confirmar_exclusao.html"
    success_url = reverse_lazy("orcamento:orcamento_list")
    modulo = "orcamento"
    acao = "excluir"


# ── Itens de Orçamento ───────────────────────

class ItemOrcamentoCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = ItemOrcamento
    form_class = ItemOrcamentoForm
    template_name = "orcamento/orcamento/item_form.html"
    modulo = "orcamento"
    acao = "editar"

    def get_success_url(self):
        return reverse_lazy("orcamento:orcamento_detail", kwargs={"pk": self.kwargs["orcamento_pk"]})

    def form_valid(self, form):
        form.instance.orcamento = Orcamento.objects.get(
            pk=self.kwargs["orcamento_pk"], empresa=self.get_empresa()
        )
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class ItemOrcamentoUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = ItemOrcamento
    form_class = ItemOrcamentoForm
    template_name = "orcamento/orcamento/item_form.html"
    modulo = "orcamento"
    acao = "editar"
    extra_context = {"titulo": "Editar Item de Orçamento"}

    def get_success_url(self):
        return reverse_lazy("orcamento:orcamento_detail", kwargs={"pk": self.object.orcamento_id})

    def get_queryset(self):
        return ItemOrcamento.objects.filter(orcamento__empresa=self.get_empresa())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class ItemOrcamentoDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = ItemOrcamento
    template_name = "orcamento/orcamento/confirmar_exclusao_item.html"
    modulo = "orcamento"
    acao = "editar"

    def get_success_url(self):
        return reverse_lazy("orcamento:orcamento_detail", kwargs={"pk": self.object.orcamento_id})

    def get_queryset(self):
        return ItemOrcamento.objects.filter(orcamento__empresa=self.get_empresa())


# ── Alertas de Estouro ───────────────────────

class AlertaEstouroOrcamentoListView(PermissaoModuloMixin, ListView):
    model = AlertaEstouroOrcamento
    template_name = "orcamento/alerta/list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "orcamento"
    acao = "ver"

    def get_queryset(self):
        return super().get_queryset().select_related(
            "item_orcamento__orcamento", "item_orcamento__plano_contas"
        ).filter(notificacao_enviada=False)