from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from apps.authentication.mixins import PermissaoModuloMixin
from .models import StatusOrcamento, Orcamento, ItemOrcamento, AlertaEstouroOrcamento
from .forms import StatusOrcamentoForm, OrcamentoForm, ItemOrcamentoForm


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

class StatusOrcamentoListView(PermissaoModuloMixin, ListView):
    model = StatusOrcamento
    template_name = "orcamento/dominio_list.html"
    context_object_name = "objetos"
    modulo = "orcamento"
    acao = "ver"
    extra_context = {
        "titulo": "Status de Orçamento",
        "create_url": "orcamento:status_create",
        "update_url": "orcamento:status_update",
        "delete_url": "orcamento:status_delete",
    }

    def get_queryset(self):
        return StatusOrcamento.objects.all().order_by("nome")


class StatusOrcamentoCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = StatusOrcamento
    form_class = StatusOrcamentoForm
    template_name = "orcamento/dominio_form.html"
    success_url = reverse_lazy("orcamento:status_list")
    modulo = "orcamento"
    acao = "criar"
    extra_context = {"titulo": "Novo Status de Orçamento", "list_url": "orcamento:status_list"}


class StatusOrcamentoUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = StatusOrcamento
    form_class = StatusOrcamentoForm
    template_name = "orcamento/dominio_form.html"
    success_url = reverse_lazy("orcamento:status_list")
    modulo = "orcamento"
    acao = "editar"
    extra_context = {"titulo": "Editar Status de Orçamento", "list_url": "orcamento:status_list"}

    def get_queryset(self):
        return StatusOrcamento.objects.all()


class StatusOrcamentoDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = StatusOrcamento
    template_name = "orcamento/dominio_confirmar_exclusao.html"
    success_url = reverse_lazy("orcamento:status_list")
    modulo = "orcamento"
    acao = "excluir"

    def get_queryset(self):
        return StatusOrcamento.objects.all()


# ══════════════════════════════════════════════
# ORÇAMENTOS
# ══════════════════════════════════════════════

class OrcamentoListView(PermissaoModuloMixin, ListView):
    model = Orcamento
    template_name = "orcamento/orcamento_list.html"
    context_object_name = "objetos"
    paginate_by = 20
    modulo = "orcamento"
    acao = "ver"

    def get_queryset(self):
        qs = (
            super().get_queryset()
            .select_related("status")
            .order_by("-ano", "nome")
        )
        if ano := self.request.GET.get("ano"):
            qs = qs.filter(ano=ano)
        if status_id := self.request.GET.get("status"):
            qs = qs.filter(status_id=status_id)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_list"] = StatusOrcamento.objects.filter(ativo=True)
        return ctx


class OrcamentoDetailView(PermissaoModuloMixin, DetailView):
    model = Orcamento
    template_name = "orcamento/orcamento_detail.html"
    context_object_name = "orcamento"
    modulo = "orcamento"
    acao = "ver"

    def get_queryset(self):
        return Orcamento.objects.filter(empresa=self.get_empresa())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        itens = (
            self.object.itens
            .select_related("plano_contas", "centro_custo")
            .order_by("mes", "plano_contas__codigo")
        )
        ctx["itens"] = itens
        ctx["alertas"] = (
            AlertaEstouroOrcamento.objects
            .filter(item_orcamento__orcamento=self.object)
            .select_related("item_orcamento__plano_contas")
            .order_by("-criado_em")
        )
        # Totais consolidados por mês para o gráfico
        from collections import defaultdict
        meses_totais = defaultdict(lambda: {"previsto": 0, "realizado": 0})
        for item in itens:
            meses_totais[item.mes]["previsto"]  += float(item.valor_previsto)
            meses_totais[item.mes]["realizado"] += float(item.valor_realizado)
        ctx["meses_totais"] = dict(sorted(meses_totais.items()))
        ctx["MESES"] = [
            "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
            "Jul", "Ago", "Set", "Out", "Nov", "Dez"
        ]
        return ctx


class OrcamentoCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = Orcamento
    form_class = OrcamentoForm
    template_name = "orcamento/orcamento_form.html"
    modulo = "orcamento"
    acao = "criar"
    extra_context = {"titulo": "Novo Orçamento"}

    def get_success_url(self):
        return reverse_lazy("orcamento:orcamento_detail", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def form_valid(self, form):
        form.instance.empresa    = self.get_empresa()
        form.instance.criado_por = self.request.user
        return super().form_valid(form)


class OrcamentoUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = Orcamento
    form_class = OrcamentoForm
    template_name = "orcamento/orcamento_form.html"
    modulo = "orcamento"
    acao = "editar"
    extra_context = {"titulo": "Editar Orçamento"}

    def get_success_url(self):
        return reverse_lazy("orcamento:orcamento_detail", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def get_queryset(self):
        return Orcamento.objects.filter(empresa=self.get_empresa())


class OrcamentoDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = Orcamento
    template_name = "orcamento/orcamento_confirmar_exclusao.html"
    success_url = reverse_lazy("orcamento:orcamento_list")
    modulo = "orcamento"
    acao = "excluir"

    def get_queryset(self):
        return Orcamento.objects.filter(empresa=self.get_empresa())


# ══════════════════════════════════════════════
# ITENS DE ORÇAMENTO
# ══════════════════════════════════════════════

class ItemOrcamentoCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = ItemOrcamento
    form_class = ItemOrcamentoForm
    template_name = "orcamento/orcamento_item_form.html"
    modulo = "orcamento"
    acao = "editar"
    extra_context = {"titulo": "Adicionar Item de Orçamento"}

    def get_success_url(self):
        return reverse_lazy("orcamento:orcamento_detail", kwargs={"pk": self.kwargs["orcamento_pk"]})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["orcamento"] = Orcamento.objects.get(
            pk=self.kwargs["orcamento_pk"], empresa=self.get_empresa()
        )
        return ctx

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def form_valid(self, form):
        form.instance.orcamento = Orcamento.objects.get(
            pk=self.kwargs["orcamento_pk"], empresa=self.get_empresa()
        )
        return super().form_valid(form)


class ItemOrcamentoUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = ItemOrcamento
    form_class = ItemOrcamentoForm
    template_name = "orcamento/orcamento_item_form.html"
    modulo = "orcamento"
    acao = "editar"
    extra_context = {"titulo": "Editar Item de Orçamento"}

    def get_success_url(self):
        return reverse_lazy("orcamento:orcamento_detail", kwargs={"pk": self.object.orcamento_id})

    def get_queryset(self):
        return ItemOrcamento.objects.filter(orcamento__empresa=self.get_empresa())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["orcamento"] = self.object.orcamento
        return ctx

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw


class ItemOrcamentoDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = ItemOrcamento
    template_name = "orcamento/orcamento_confirmar_exclusao_item.html"
    modulo = "orcamento"
    acao = "editar"

    def get_success_url(self):
        return reverse_lazy("orcamento:orcamento_detail", kwargs={"pk": self.object.orcamento_id})

    def get_queryset(self):
        return ItemOrcamento.objects.filter(orcamento__empresa=self.get_empresa())


# ══════════════════════════════════════════════
# ALERTAS DE ESTOURO
# ══════════════════════════════════════════════

class AlertaEstouroOrcamentoListView(PermissaoModuloMixin, ListView):
    model = AlertaEstouroOrcamento
    template_name = "orcamento/alerta_list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "orcamento"
    acao = "ver"

    def get_queryset(self):
        qs = (
            super().get_queryset()
            .select_related(
                "item_orcamento__orcamento",
                "item_orcamento__plano_contas",
                "item_orcamento__centro_custo",
            )
            .filter(empresa=self.get_empresa())
            .order_by("-criado_em")
        )
        # Filtro por notificação pendente/enviada
        if notif := self.request.GET.get("notificacao"):
            if notif in ("true", "false"):
                qs = qs.filter(notificacao_enviada=(notif == "true"))
        return qs