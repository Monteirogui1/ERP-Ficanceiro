from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from apps.authentication.mixins import PermissaoModuloMixin
from apps.sistema.models import ContaBancaria
from .models import (
    TipoDocumentoFinanceiro, TipoLancamento, FormaPagamento,
    StatusContaPagar, StatusContaReceber,
    PeriodicidadeRecorrencia, TipoEncargo, TipoCenarioFluxo,
    ContaPagar, EncargoContaPagar, DocumentoContaPagar, AprovacaoContaPagar,
    ContaReceber, EncargoContaReceber, DocumentoContaReceber,
    LancamentoFinanceiro, TransferenciaBancaria, ProjecaoFluxoCaixa,
)
from .forms import (
    TipoDocumentoFinanceiroForm, FormaPagamentoForm,
    StatusContaPagarForm, StatusContaReceberForm,
    PeriodicidadeRecorrenciaForm, TipoEncargoForm, TipoCenarioFluxoForm,
    ContaPagarForm, EncargoContaPagarForm, DocumentoContaPagarForm,
    ContaReceberForm, EncargoContaReceberForm, DocumentoContaReceberForm,
    LancamentoFinanceiroForm, TransferenciaBancariaForm,
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

class TipoDocumentoFinanceiroListView(PermissaoModuloMixin, ListView):
    model = TipoDocumentoFinanceiro
    template_name = "financeiro/dominio_list.html"
    context_object_name = "objetos"
    modulo = "financeiro"
    acao = "ver"
    extra_context = {
        "titulo": "Tipos de Documento Financeiro",
        "create_url": "financeiro:tipo_documento_create",
        "update_url": "financeiro:tipo_documento_update",
        "delete_url": "financeiro:tipo_documento_delete",
    }

    def get_queryset(self):
        return TipoDocumentoFinanceiro.objects.filter(empresa=self.get_empresa()).order_by("nome")


class TipoDocumentoFinanceiroCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = TipoDocumentoFinanceiro
    form_class = TipoDocumentoFinanceiroForm
    template_name = "financeiro/dominio_form.html"
    success_url = reverse_lazy("financeiro:tipo_documento_list")
    modulo = "financeiro"
    acao = "criar"
    extra_context = {"titulo": "Novo Tipo de Documento", "list_url": "financeiro:tipo_documento_list"}

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        return super().form_valid(form)


class TipoDocumentoFinanceiroUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = TipoDocumentoFinanceiro
    form_class = TipoDocumentoFinanceiroForm
    template_name = "financeiro/dominio_form.html"
    success_url = reverse_lazy("financeiro:tipo_documento_list")
    modulo = "financeiro"
    acao = "editar"
    extra_context = {"titulo": "Editar Tipo de Documento", "list_url": "financeiro:tipo_documento_list"}

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def get_queryset(self):
        return TipoDocumentoFinanceiro.objects.filter(empresa=self.get_empresa())


class TipoDocumentoFinanceiroDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = TipoDocumentoFinanceiro
    template_name = "financeiro/dominio_confirmar_exclusao.html"
    success_url = reverse_lazy("financeiro:tipo_documento_list")
    modulo = "financeiro"
    acao = "excluir"

    def get_queryset(self):
        return TipoDocumentoFinanceiro.objects.filter(empresa=self.get_empresa())


class FormaPagamentoListView(PermissaoModuloMixin, ListView):
    model = FormaPagamento
    template_name = "financeiro/dominio_list.html"
    context_object_name = "objetos"
    modulo = "financeiro"
    acao = "ver"
    extra_context = {
        "titulo": "Formas de Pagamento",
        "create_url": "financeiro:forma_pagamento_create",
        "update_url": "financeiro:forma_pagamento_update",
        "delete_url": "financeiro:forma_pagamento_delete",
    }

    def get_queryset(self):
        return FormaPagamento.objects.filter(empresa=self.get_empresa()).order_by("nome")


class FormaPagamentoCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = FormaPagamento
    form_class = FormaPagamentoForm
    template_name = "financeiro/dominio_form.html"
    success_url = reverse_lazy("financeiro:forma_pagamento_list")
    modulo = "financeiro"
    acao = "criar"
    extra_context = {"titulo": "Nova Forma de Pagamento", "list_url": "financeiro:forma_pagamento_list"}

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        return super().form_valid(form)


class FormaPagamentoUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = FormaPagamento
    form_class = FormaPagamentoForm
    template_name = "financeiro/dominio_form.html"
    success_url = reverse_lazy("financeiro:forma_pagamento_list")
    modulo = "financeiro"
    acao = "editar"
    extra_context = {"titulo": "Editar Forma de Pagamento", "list_url": "financeiro:forma_pagamento_list"}

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def get_queryset(self):
        return FormaPagamento.objects.filter(empresa=self.get_empresa())


class FormaPagamentoDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = FormaPagamento
    template_name = "financeiro/dominio_confirmar_exclusao.html"
    success_url = reverse_lazy("financeiro:forma_pagamento_list")
    modulo = "financeiro"
    acao = "excluir"

    def get_queryset(self):
        return FormaPagamento.objects.filter(empresa=self.get_empresa())


class StatusContaPagarListView(PermissaoModuloMixin, ListView):
    model = StatusContaPagar
    template_name = "financeiro/dominio_list.html"
    context_object_name = "objetos"
    modulo = "financeiro"
    acao = "ver"
    extra_context = {
        "titulo": "Status de Conta a Pagar",
        "create_url": "financeiro:status_conta_pagar_create",
        "update_url": "financeiro:status_conta_pagar_update",
        "delete_url": "financeiro:status_conta_pagar_delete",
    }

    def get_queryset(self):
        return StatusContaPagar.objects.all().order_by("nome")


class StatusContaPagarCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = StatusContaPagar
    form_class = StatusContaPagarForm
    template_name = "financeiro/dominio_form.html"
    success_url = reverse_lazy("financeiro:status_conta_pagar_list")
    modulo = "financeiro"
    acao = "criar"
    extra_context = {"titulo": "Novo Status de Conta a Pagar", "list_url": "financeiro:status_conta_pagar_list"}


class StatusContaPagarUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = StatusContaPagar
    form_class = StatusContaPagarForm
    template_name = "financeiro/dominio_form.html"
    success_url = reverse_lazy("financeiro:status_conta_pagar_list")
    modulo = "financeiro"
    acao = "editar"
    extra_context = {"titulo": "Editar Status de Conta a Pagar", "list_url": "financeiro:status_conta_pagar_list"}

    def get_queryset(self):
        return StatusContaPagar.objects.all()


class StatusContaPagarDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = StatusContaPagar
    template_name = "financeiro/dominio_confirmar_exclusao.html"
    success_url = reverse_lazy("financeiro:status_conta_pagar_list")
    modulo = "financeiro"
    acao = "excluir"

    def get_queryset(self):
        return StatusContaPagar.objects.all()


class StatusContaReceberListView(PermissaoModuloMixin, ListView):
    model = StatusContaReceber
    template_name = "financeiro/dominio_list.html"
    context_object_name = "objetos"
    modulo = "financeiro"
    acao = "ver"
    extra_context = {
        "titulo": "Status de Conta a Receber",
        "create_url": "financeiro:status_conta_receber_create",
        "update_url": "financeiro:status_conta_receber_update",
        "delete_url": "financeiro:status_conta_receber_delete",
    }

    def get_queryset(self):
        return StatusContaReceber.objects.all().order_by("nome")


class StatusContaReceberCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = StatusContaReceber
    form_class = StatusContaReceberForm
    template_name = "financeiro/dominio_form.html"
    success_url = reverse_lazy("financeiro:status_conta_receber_list")
    modulo = "financeiro"
    acao = "criar"
    extra_context = {"titulo": "Novo Status de Conta a Receber", "list_url": "financeiro:status_conta_receber_list"}


class StatusContaReceberUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = StatusContaReceber
    form_class = StatusContaReceberForm
    template_name = "financeiro/dominio_form.html"
    success_url = reverse_lazy("financeiro:status_conta_receber_list")
    modulo = "financeiro"
    acao = "editar"
    extra_context = {"titulo": "Editar Status de Conta a Receber", "list_url": "financeiro:status_conta_receber_list"}

    def get_queryset(self):
        return StatusContaReceber.objects.all()


class StatusContaReceberDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = StatusContaReceber
    template_name = "financeiro/dominio_confirmar_exclusao.html"
    success_url = reverse_lazy("financeiro:status_conta_receber_list")
    modulo = "financeiro"
    acao = "excluir"

    def get_queryset(self):
        return StatusContaReceber.objects.all()


class PeriodicidadeRecorrenciaListView(PermissaoModuloMixin, ListView):
    model = PeriodicidadeRecorrencia
    template_name = "financeiro/dominio_list.html"
    context_object_name = "objetos"
    modulo = "financeiro"
    acao = "ver"
    extra_context = {
        "titulo": "Periodicidades de Recorrência",
        "create_url": "financeiro:periodicidade_create",
        "update_url": "financeiro:periodicidade_update",
        "delete_url": "financeiro:periodicidade_delete",
    }

    def get_queryset(self):
        return PeriodicidadeRecorrencia.objects.all().order_by("nome")


class PeriodicidadeRecorrenciaCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = PeriodicidadeRecorrencia
    form_class = PeriodicidadeRecorrenciaForm
    template_name = "financeiro/dominio_form.html"
    success_url = reverse_lazy("financeiro:periodicidade_list")
    modulo = "financeiro"
    acao = "criar"
    extra_context = {"titulo": "Nova Periodicidade", "list_url": "financeiro:periodicidade_list"}


class PeriodicidadeRecorrenciaUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = PeriodicidadeRecorrencia
    form_class = PeriodicidadeRecorrenciaForm
    template_name = "financeiro/dominio_form.html"
    success_url = reverse_lazy("financeiro:periodicidade_list")
    modulo = "financeiro"
    acao = "editar"
    extra_context = {"titulo": "Editar Periodicidade", "list_url": "financeiro:periodicidade_list"}

    def get_queryset(self):
        return PeriodicidadeRecorrencia.objects.all()


class PeriodicidadeRecorrenciaDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = PeriodicidadeRecorrencia
    template_name = "financeiro/dominio_confirmar_exclusao.html"
    success_url = reverse_lazy("financeiro:periodicidade_list")
    modulo = "financeiro"
    acao = "excluir"

    def get_queryset(self):
        return PeriodicidadeRecorrencia.objects.all()


class TipoEncargoListView(PermissaoModuloMixin, ListView):
    model = TipoEncargo
    template_name = "financeiro/dominio_list.html"
    context_object_name = "objetos"
    modulo = "financeiro"
    acao = "ver"
    extra_context = {
        "titulo": "Tipos de Encargo",
        "create_url": "financeiro:tipo_encargo_create",
        "update_url": "financeiro:tipo_encargo_update",
        "delete_url": "financeiro:tipo_encargo_delete",
    }

    def get_queryset(self):
        return TipoEncargo.objects.all().order_by("nome")


class TipoEncargoCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = TipoEncargo
    form_class = TipoEncargoForm
    template_name = "financeiro/dominio_form.html"
    success_url = reverse_lazy("financeiro:tipo_encargo_list")
    modulo = "financeiro"
    acao = "criar"
    extra_context = {"titulo": "Novo Tipo de Encargo", "list_url": "financeiro:tipo_encargo_list"}


class TipoEncargoUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = TipoEncargo
    form_class = TipoEncargoForm
    template_name = "financeiro/dominio_form.html"
    success_url = reverse_lazy("financeiro:tipo_encargo_list")
    modulo = "financeiro"
    acao = "editar"
    extra_context = {"titulo": "Editar Tipo de Encargo", "list_url": "financeiro:tipo_encargo_list"}

    def get_queryset(self):
        return TipoEncargo.objects.all()


class TipoEncargoDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = TipoEncargo
    template_name = "financeiro/dominio_confirmar_exclusao.html"
    success_url = reverse_lazy("financeiro:tipo_encargo_list")
    modulo = "financeiro"
    acao = "excluir"

    def get_queryset(self):
        return TipoEncargo.objects.all()


class TipoCenarioFluxoListView(PermissaoModuloMixin, ListView):
    model = TipoCenarioFluxo
    template_name = "financeiro/dominio_list.html"
    context_object_name = "objetos"
    modulo = "financeiro"
    acao = "ver"
    extra_context = {
        "titulo": "Cenários de Fluxo de Caixa",
        "create_url": "financeiro:tipo_cenario_fluxo_create",
        "update_url": "financeiro:tipo_cenario_fluxo_update",
        "delete_url": "financeiro:tipo_cenario_fluxo_delete",
    }

    def get_queryset(self):
        return TipoCenarioFluxo.objects.all().order_by("nome")


class TipoCenarioFluxoCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = TipoCenarioFluxo
    form_class = TipoCenarioFluxoForm
    template_name = "financeiro/dominio_form.html"
    success_url = reverse_lazy("financeiro:tipo_cenario_fluxo_list")
    modulo = "financeiro"
    acao = "criar"
    extra_context = {"titulo": "Novo Cenário de Fluxo", "list_url": "financeiro:tipo_cenario_fluxo_list"}


class TipoCenarioFluxoUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = TipoCenarioFluxo
    form_class = TipoCenarioFluxoForm
    template_name = "financeiro/dominio_form.html"
    success_url = reverse_lazy("financeiro:tipo_cenario_fluxo_list")
    modulo = "financeiro"
    acao = "editar"
    extra_context = {"titulo": "Editar Cenário de Fluxo", "list_url": "financeiro:tipo_cenario_fluxo_list"}

    def get_queryset(self):
        return TipoCenarioFluxo.objects.all()


class TipoCenarioFluxoDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = TipoCenarioFluxo
    template_name = "financeiro/dominio_confirmar_exclusao.html"
    success_url = reverse_lazy("financeiro:tipo_cenario_fluxo_list")
    modulo = "financeiro"
    acao = "excluir"

    def get_queryset(self):
        return TipoCenarioFluxo.objects.all()


# ══════════════════════════════════════════════
# CONTAS A PAGAR
# ══════════════════════════════════════════════

class ContaPagarListView(PermissaoModuloMixin, ListView):
    model = ContaPagar
    template_name = "financeiro/conta_pagar_list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "contas_pagar"
    acao = "ver"

    def get_queryset(self):
        qs = (
            super().get_queryset()
            .select_related("fornecedor", "status", "plano_contas", "forma_pagamento")
            .order_by("data_vencimento")
        )
        if status_id := self.request.GET.get("status"):
            qs = qs.filter(status_id=status_id)
        if venc_de := self.request.GET.get("vencimento_de"):
            qs = qs.filter(data_vencimento__gte=venc_de)
        if venc_ate := self.request.GET.get("vencimento_ate"):
            qs = qs.filter(data_vencimento__lte=venc_ate)
        if q := self.request.GET.get("q"):
            qs = qs.filter(descricao__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_list"] = StatusContaPagar.objects.filter(ativo=True)
        ctx["hoje"] = timezone.now().date()
        return ctx


class ContaPagarDetailView(PermissaoModuloMixin, DetailView):
    model = ContaPagar
    template_name = "financeiro/conta_pagar_detail.html"
    context_object_name = "conta"
    modulo = "contas_pagar"
    acao = "ver"

    def get_queryset(self):
        return ContaPagar.objects.filter(empresa=self.get_empresa())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["encargos"]   = self.object.encargos.select_related("tipo_encargo").all()
        ctx["documentos"] = self.object.documentos.all()
        ctx["aprovacoes"] = self.object.historico_aprovacoes.select_related("usuario").all()
        ctx["parcelas"]   = self.object.parcelas.order_by("numero_parcela_atual")
        ctx["hoje"]       = timezone.now().date()
        return ctx


class ContaPagarCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = ContaPagar
    form_class = ContaPagarForm
    template_name = "financeiro/conta_pagar_form.html"
    modulo = "contas_pagar"
    acao = "criar"
    extra_context = {"titulo": "Nova Conta a Pagar"}

    def get_success_url(self):
        return reverse_lazy("financeiro:conta_pagar_detail", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def form_valid(self, form):
        form.instance.empresa    = self.get_empresa()
        form.instance.criado_por = self.request.user
        return super().form_valid(form)


class ContaPagarUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = ContaPagar
    form_class = ContaPagarForm
    template_name = "financeiro/conta_pagar_form.html"
    modulo = "contas_pagar"
    acao = "editar"
    extra_context = {"titulo": "Editar Conta a Pagar"}

    def get_success_url(self):
        return reverse_lazy("financeiro:conta_pagar_detail", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def get_queryset(self):
        return ContaPagar.objects.filter(empresa=self.get_empresa())


class ContaPagarDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = ContaPagar
    template_name = "financeiro/conta_pagar_confirmar_exclusao.html"
    success_url = reverse_lazy("financeiro:conta_pagar_list")
    modulo = "contas_pagar"
    acao = "excluir"

    def get_queryset(self):
        return ContaPagar.objects.filter(empresa=self.get_empresa())


class EncargoContaPagarCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = EncargoContaPagar
    form_class = EncargoContaPagarForm
    template_name = "financeiro/conta_pagar_encargo_form.html"
    modulo = "contas_pagar"
    acao = "editar"

    def get_success_url(self):
        return reverse_lazy("financeiro:conta_pagar_detail", kwargs={"pk": self.kwargs["conta_pk"]})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["conta"] = ContaPagar.objects.get(pk=self.kwargs["conta_pk"], empresa=self.get_empresa())
        return ctx

    def form_valid(self, form):
        form.instance.conta_pagar = ContaPagar.objects.get(
            pk=self.kwargs["conta_pk"], empresa=self.get_empresa()
        )
        return super().form_valid(form)


class EncargoContaPagarDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = EncargoContaPagar
    template_name = "financeiro/conta_pagar_confirmar_exclusao_encargo.html"
    modulo = "contas_pagar"
    acao = "editar"

    def get_queryset(self):
        return EncargoContaPagar.objects.filter(conta_pagar__empresa=self.get_empresa())

    def get_success_url(self):
        return reverse_lazy("financeiro:conta_pagar_detail", kwargs={"pk": self.object.conta_pagar_id})


class DocumentoContaPagarCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = DocumentoContaPagar
    form_class = DocumentoContaPagarForm
    template_name = "financeiro/conta_pagar_documento_form.html"
    modulo = "contas_pagar"
    acao = "editar"

    def get_success_url(self):
        return reverse_lazy("financeiro:conta_pagar_detail", kwargs={"pk": self.kwargs["conta_pk"]})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["conta"] = ContaPagar.objects.get(pk=self.kwargs["conta_pk"], empresa=self.get_empresa())
        return ctx

    def form_valid(self, form):
        form.instance.conta_pagar = ContaPagar.objects.get(
            pk=self.kwargs["conta_pk"], empresa=self.get_empresa()
        )
        form.instance.enviado_por = self.request.user
        if form.instance.arquivo:
            form.instance.tamanho_bytes = form.instance.arquivo.size
            form.instance.tipo_arquivo  = form.instance.arquivo.name.split(".")[-1].upper()
        return super().form_valid(form)


class DocumentoContaPagarDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = DocumentoContaPagar
    template_name = "financeiro/conta_pagar_confirmar_exclusao_documento.html"
    modulo = "contas_pagar"
    acao = "editar"

    def get_queryset(self):
        return DocumentoContaPagar.objects.filter(conta_pagar__empresa=self.get_empresa())

    def get_success_url(self):
        return reverse_lazy("financeiro:conta_pagar_detail", kwargs={"pk": self.object.conta_pagar_id})


class AprovacaoContaPagarCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    """Registra aprovação ou rejeição na cadeia multinível."""
    model = AprovacaoContaPagar
    template_name = "financeiro/conta_pagar_aprovacao_form.html"
    fields = ["decisao", "justificativa"]
    modulo = "contas_pagar"
    acao = "criar"

    def get_success_url(self):
        return reverse_lazy("financeiro:conta_pagar_detail", kwargs={"pk": self.kwargs["conta_pk"]})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["conta"] = ContaPagar.objects.get(pk=self.kwargs["conta_pk"], empresa=self.get_empresa())
        return ctx

    def form_valid(self, form):
        conta  = ContaPagar.objects.get(pk=self.kwargs["conta_pk"], empresa=self.get_empresa())
        perfil = getattr(self.request.user, "perfil_acesso", None)
        form.instance.conta_pagar     = conta
        form.instance.usuario         = self.request.user
        form.instance.nivel_aprovacao = perfil.nivel_aprovacao if perfil else 1
        if form.instance.decisao == "APROVADO":
            conta.aprovado_por   = self.request.user
            conta.data_aprovacao = timezone.now()
            conta.save(update_fields=["aprovado_por", "data_aprovacao"])
        return super().form_valid(form)


# ══════════════════════════════════════════════
# CONTAS A RECEBER
# ══════════════════════════════════════════════

class ContaReceberListView(PermissaoModuloMixin, ListView):
    model = ContaReceber
    template_name = "financeiro/conta_receber_list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "contas_receber"
    acao = "ver"

    def get_queryset(self):
        qs = (
            super().get_queryset()
            .select_related("cliente", "status", "forma_pagamento")
            .order_by("data_vencimento")
        )
        if status_id := self.request.GET.get("status"):
            qs = qs.filter(status_id=status_id)
        if venc_de := self.request.GET.get("vencimento_de"):
            qs = qs.filter(data_vencimento__gte=venc_de)
        if venc_ate := self.request.GET.get("vencimento_ate"):
            qs = qs.filter(data_vencimento__lte=venc_ate)
        if self.request.GET.get("inadimplente") == "true":
            qs = qs.filter(cliente__inadimplente=True)
        if q := self.request.GET.get("q"):
            qs = qs.filter(descricao__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_list"] = StatusContaReceber.objects.filter(ativo=True)
        ctx["hoje"] = timezone.now().date()
        return ctx


class ContaReceberDetailView(PermissaoModuloMixin, DetailView):
    model = ContaReceber
    template_name = "financeiro/conta_receber_detail.html"
    context_object_name = "conta"
    modulo = "contas_receber"
    acao = "ver"

    def get_queryset(self):
        return ContaReceber.objects.filter(empresa=self.get_empresa())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["encargos"]   = self.object.encargos.select_related("tipo_encargo").all()
        ctx["documentos"] = self.object.documentos.all()
        ctx["parcelas"]   = self.object.parcelas.order_by("numero_parcela_atual")
        ctx["hoje"]       = timezone.now().date()
        return ctx


class ContaReceberCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = ContaReceber
    form_class = ContaReceberForm
    template_name = "financeiro/conta_receber_form.html"
    modulo = "contas_receber"
    acao = "criar"
    extra_context = {"titulo": "Nova Conta a Receber"}

    def get_success_url(self):
        return reverse_lazy("financeiro:conta_receber_detail", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def form_valid(self, form):
        form.instance.empresa    = self.get_empresa()
        form.instance.criado_por = self.request.user
        return super().form_valid(form)


class ContaReceberUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = ContaReceber
    form_class = ContaReceberForm
    template_name = "financeiro/conta_receber_form.html"
    modulo = "contas_receber"
    acao = "editar"
    extra_context = {"titulo": "Editar Conta a Receber"}

    def get_success_url(self):
        return reverse_lazy("financeiro:conta_receber_detail", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def get_queryset(self):
        return ContaReceber.objects.filter(empresa=self.get_empresa())


class ContaReceberDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = ContaReceber
    template_name = "financeiro/conta_receber_confirmar_exclusao.html"
    success_url = reverse_lazy("financeiro:conta_receber_list")
    modulo = "contas_receber"
    acao = "excluir"

    def get_queryset(self):
        return ContaReceber.objects.filter(empresa=self.get_empresa())


class EncargoContaReceberCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = EncargoContaReceber
    form_class = EncargoContaReceberForm
    template_name = "financeiro/conta_receber_encargo_form.html"
    modulo = "contas_receber"
    acao = "editar"

    def get_success_url(self):
        return reverse_lazy("financeiro:conta_receber_detail", kwargs={"pk": self.kwargs["conta_pk"]})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["conta"] = ContaReceber.objects.get(pk=self.kwargs["conta_pk"], empresa=self.get_empresa())
        return ctx

    def form_valid(self, form):
        form.instance.conta_receber = ContaReceber.objects.get(
            pk=self.kwargs["conta_pk"], empresa=self.get_empresa()
        )
        return super().form_valid(form)


class EncargoContaReceberDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = EncargoContaReceber
    template_name = "financeiro/conta_receber_confirmar_exclusao_encargo.html"
    modulo = "contas_receber"
    acao = "editar"

    def get_queryset(self):
        return EncargoContaReceber.objects.filter(conta_receber__empresa=self.get_empresa())

    def get_success_url(self):
        return reverse_lazy("financeiro:conta_receber_detail", kwargs={"pk": self.object.conta_receber_id})


class DocumentoContaReceberCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = DocumentoContaReceber
    form_class = DocumentoContaReceberForm
    template_name = "financeiro/conta_receber_documento_form.html"
    modulo = "contas_receber"
    acao = "editar"

    def get_success_url(self):
        return reverse_lazy("financeiro:conta_receber_detail", kwargs={"pk": self.kwargs["conta_pk"]})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["conta"] = ContaReceber.objects.get(pk=self.kwargs["conta_pk"], empresa=self.get_empresa())
        return ctx

    def form_valid(self, form):
        form.instance.conta_receber = ContaReceber.objects.get(
            pk=self.kwargs["conta_pk"], empresa=self.get_empresa()
        )
        form.instance.enviado_por = self.request.user
        if form.instance.arquivo:
            form.instance.tamanho_bytes = form.instance.arquivo.size
            form.instance.tipo_arquivo  = form.instance.arquivo.name.split(".")[-1].upper()
        return super().form_valid(form)


class DocumentoContaReceberDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = DocumentoContaReceber
    template_name = "financeiro/conta_receber_confirmar_exclusao_documento.html"
    modulo = "contas_receber"
    acao = "editar"

    def get_queryset(self):
        return DocumentoContaReceber.objects.filter(conta_receber__empresa=self.get_empresa())

    def get_success_url(self):
        return reverse_lazy("financeiro:conta_receber_detail", kwargs={"pk": self.object.conta_receber_id})


# ══════════════════════════════════════════════
# LANÇAMENTOS FINANCEIROS
# ══════════════════════════════════════════════

class LancamentoFinanceiroListView(PermissaoModuloMixin, ListView):
    model = LancamentoFinanceiro
    template_name = "financeiro/lancamento_list.html"
    context_object_name = "objetos"
    paginate_by = 50
    modulo = "fluxo_caixa"
    acao = "ver"

    def get_queryset(self):
        qs = (
            super().get_queryset()
            .select_related("conta_bancaria", "tipo_lancamento", "plano_contas", "centro_custo")
            .order_by("-data_lancamento")
        )
        if conta_id := self.request.GET.get("conta_bancaria"):
            qs = qs.filter(conta_bancaria_id=conta_id)
        if data_de := self.request.GET.get("data_de"):
            qs = qs.filter(data_lancamento__gte=data_de)
        if data_ate := self.request.GET.get("data_ate"):
            qs = qs.filter(data_lancamento__lte=data_ate)
        if conciliado := self.request.GET.get("conciliado"):
            if conciliado in ("true", "false"):
                qs = qs.filter(conciliado=(conciliado == "true"))
        if q := self.request.GET.get("q"):
            qs = qs.filter(descricao__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["contas_bancarias"] = ContaBancaria.objects.filter(
            empresa=self.get_empresa(), ativo=True
        )
        return ctx


class LancamentoFinanceiroCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = LancamentoFinanceiro
    form_class = LancamentoFinanceiroForm
    template_name = "financeiro/lancamento_form.html"
    success_url = reverse_lazy("financeiro:lancamento_list")
    modulo = "fluxo_caixa"
    acao = "criar"
    extra_context = {"titulo": "Novo Lançamento"}

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def form_valid(self, form):
        form.instance.empresa    = self.get_empresa()
        form.instance.criado_por = self.request.user
        return super().form_valid(form)


class LancamentoFinanceiroUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = LancamentoFinanceiro
    form_class = LancamentoFinanceiroForm
    template_name = "financeiro/lancamento_form.html"
    success_url = reverse_lazy("financeiro:lancamento_list")
    modulo = "fluxo_caixa"
    acao = "editar"
    extra_context = {"titulo": "Editar Lançamento"}

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def get_queryset(self):
        return LancamentoFinanceiro.objects.filter(empresa=self.get_empresa())


class LancamentoFinanceiroDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = LancamentoFinanceiro
    template_name = "financeiro/lancamento_confirmar_exclusao.html"
    success_url = reverse_lazy("financeiro:lancamento_list")
    modulo = "fluxo_caixa"
    acao = "excluir"

    def get_queryset(self):
        return LancamentoFinanceiro.objects.filter(empresa=self.get_empresa())


# ══════════════════════════════════════════════
# TRANSFERÊNCIAS BANCÁRIAS
# ══════════════════════════════════════════════

class TransferenciaBancariaListView(PermissaoModuloMixin, ListView):
    model = TransferenciaBancaria
    template_name = "financeiro/transferencia_list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "fluxo_caixa"
    acao = "ver"

    def get_queryset(self):
        qs = (
            super().get_queryset()
            .select_related("conta_origem", "conta_destino")
            .order_by("-data_transferencia")
        )
        if data_de := self.request.GET.get("data_de"):
            qs = qs.filter(data_transferencia__gte=data_de)
        if data_ate := self.request.GET.get("data_ate"):
            qs = qs.filter(data_transferencia__lte=data_ate)
        return qs


class TransferenciaBancariaCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = TransferenciaBancaria
    form_class = TransferenciaBancariaForm
    template_name = "financeiro/transferencia_form.html"
    success_url = reverse_lazy("financeiro:transferencia_list")
    modulo = "fluxo_caixa"
    acao = "criar"
    extra_context = {"titulo": "Nova Transferência Bancária"}

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def form_valid(self, form):
        form.instance.empresa    = self.get_empresa()
        form.instance.criado_por = self.request.user
        return super().form_valid(form)


class TransferenciaBancariaDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = TransferenciaBancaria
    template_name = "financeiro/transferencia_confirmar_exclusao.html"
    success_url = reverse_lazy("financeiro:transferencia_list")
    modulo = "fluxo_caixa"
    acao = "excluir"

    def get_queryset(self):
        return TransferenciaBancaria.objects.filter(empresa=self.get_empresa())


# ══════════════════════════════════════════════
# PROJEÇÃO DE FLUXO DE CAIXA
# ══════════════════════════════════════════════

class ProjecaoFluxoCaixaListView(PermissaoModuloMixin, ListView):
    model = ProjecaoFluxoCaixa
    template_name = "financeiro/projecao_list.html"
    context_object_name = "objetos"
    modulo = "fluxo_caixa"
    acao = "ver"

    def get_queryset(self):
        return (
            super().get_queryset()
            .select_related("cenario", "conta_bancaria")
            .order_by("data_referencia")
        )


class ProjecaoFluxoCaixaCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = ProjecaoFluxoCaixa
    template_name = "financeiro/projecao_form.html"
    fields = [
        "conta_bancaria", "cenario", "data_referencia",
        "entradas_previstas", "saidas_previstas", "saldo_projetado",
    ]
    success_url = reverse_lazy("financeiro:projecao_list")
    modulo = "fluxo_caixa"
    acao = "criar"
    extra_context = {"titulo": "Nova Projeção de Fluxo"}

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        return super().form_valid(form)


class ProjecaoFluxoCaixaDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = ProjecaoFluxoCaixa
    template_name = "financeiro/projecao_confirmar_exclusao.html"
    success_url = reverse_lazy("financeiro:projecao_list")
    modulo = "fluxo_caixa"
    acao = "excluir"

    def get_queryset(self):
        return ProjecaoFluxoCaixa.objects.filter(empresa=self.get_empresa())