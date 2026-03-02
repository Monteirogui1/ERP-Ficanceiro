from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from apps.authentication.mixins import PermissaoModuloMixin
from apps.sistema.models import ContaBancaria
from .models import (
    TipoDocumentoFinanceiro, FormaPagamento,
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
# TABELAS DE DOMÍNIO
# ══════════════════════════════════════════════

class TipoDocumentoFinanceiroListView(PermissaoModuloMixin, ListView):
    model = TipoDocumentoFinanceiro
    template_name = "financeiro/dominio/tipo_documento_list.html"
    context_object_name = "objetos"
    modulo = "financeiro"
    acao = "ver"


class TipoDocumentoFinanceiroCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = TipoDocumentoFinanceiro
    form_class = TipoDocumentoFinanceiroForm
    template_name = "financeiro/dominio/form.html"
    success_url = reverse_lazy("financeiro:tipo_documento_list")
    modulo = "financeiro"
    acao = "criar"
    extra_context = {"titulo": "Novo Tipo de Documento Financeiro"}


class TipoDocumentoFinanceiroUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = TipoDocumentoFinanceiro
    form_class = TipoDocumentoFinanceiroForm
    template_name = "financeiro/dominio/form.html"
    success_url = reverse_lazy("financeiro:tipo_documento_list")
    modulo = "financeiro"
    acao = "editar"
    extra_context = {"titulo": "Editar Tipo de Documento Financeiro"}


class TipoDocumentoFinanceiroDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = TipoDocumentoFinanceiro
    template_name = "financeiro/dominio/confirmar_exclusao.html"
    success_url = reverse_lazy("financeiro:tipo_documento_list")
    modulo = "financeiro"
    acao = "excluir"


class FormaPagamentoListView(PermissaoModuloMixin, ListView):
    model = FormaPagamento
    template_name = "financeiro/dominio/forma_pagamento_list.html"
    context_object_name = "objetos"
    modulo = "financeiro"
    acao = "ver"


class FormaPagamentoCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = FormaPagamento
    form_class = FormaPagamentoForm
    template_name = "financeiro/dominio/form.html"
    success_url = reverse_lazy("financeiro:forma_pagamento_list")
    modulo = "financeiro"
    acao = "criar"
    extra_context = {"titulo": "Nova Forma de Pagamento"}


class FormaPagamentoUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = FormaPagamento
    form_class = FormaPagamentoForm
    template_name = "financeiro/dominio/form.html"
    success_url = reverse_lazy("financeiro:forma_pagamento_list")
    modulo = "financeiro"
    acao = "editar"
    extra_context = {"titulo": "Editar Forma de Pagamento"}


class FormaPagamentoDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = FormaPagamento
    template_name = "financeiro/dominio/confirmar_exclusao.html"
    success_url = reverse_lazy("financeiro:forma_pagamento_list")
    modulo = "financeiro"
    acao = "excluir"


class StatusContaPagarListView(PermissaoModuloMixin, ListView):
    model = StatusContaPagar
    template_name = "financeiro/dominio/status_conta_pagar_list.html"
    context_object_name = "objetos"
    modulo = "financeiro"
    acao = "ver"

    def get_queryset(self):
        return StatusContaPagar.objects.all()


class StatusContaPagarCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = StatusContaPagar
    form_class = StatusContaPagarForm
    template_name = "financeiro/dominio/form.html"
    success_url = reverse_lazy("financeiro:status_conta_pagar_list")
    modulo = "financeiro"
    acao = "criar"
    extra_context = {"titulo": "Novo Status de Conta a Pagar"}


class StatusContaPagarUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = StatusContaPagar
    form_class = StatusContaPagarForm
    template_name = "financeiro/dominio/form.html"
    success_url = reverse_lazy("financeiro:status_conta_pagar_list")
    modulo = "financeiro"
    acao = "editar"
    extra_context = {"titulo": "Editar Status de Conta a Pagar"}

    def get_queryset(self):
        return StatusContaPagar.objects.all()


class StatusContaPagarDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = StatusContaPagar
    template_name = "financeiro/dominio/confirmar_exclusao.html"
    success_url = reverse_lazy("financeiro:status_conta_pagar_list")
    modulo = "financeiro"
    acao = "excluir"

    def get_queryset(self):
        return StatusContaPagar.objects.all()


class StatusContaReceberListView(PermissaoModuloMixin, ListView):
    model = StatusContaReceber
    template_name = "financeiro/dominio/status_conta_receber_list.html"
    context_object_name = "objetos"
    modulo = "financeiro"
    acao = "ver"

    def get_queryset(self):
        return StatusContaReceber.objects.all()


class StatusContaReceberCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = StatusContaReceber
    form_class = StatusContaReceberForm
    template_name = "financeiro/dominio/form.html"
    success_url = reverse_lazy("financeiro:status_conta_receber_list")
    modulo = "financeiro"
    acao = "criar"
    extra_context = {"titulo": "Novo Status de Conta a Receber"}


class StatusContaReceberUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = StatusContaReceber
    form_class = StatusContaReceberForm
    template_name = "financeiro/dominio/form.html"
    success_url = reverse_lazy("financeiro:status_conta_receber_list")
    modulo = "financeiro"
    acao = "editar"
    extra_context = {"titulo": "Editar Status de Conta a Receber"}

    def get_queryset(self):
        return StatusContaReceber.objects.all()


class StatusContaReceberDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = StatusContaReceber
    template_name = "financeiro/dominio/confirmar_exclusao.html"
    success_url = reverse_lazy("financeiro:status_conta_receber_list")
    modulo = "financeiro"
    acao = "excluir"

    def get_queryset(self):
        return StatusContaReceber.objects.all()


class PeriodicidadeRecorrenciaListView(PermissaoModuloMixin, ListView):
    model = PeriodicidadeRecorrencia
    template_name = "financeiro/dominio/periodicidade_list.html"
    context_object_name = "objetos"
    modulo = "financeiro"
    acao = "ver"

    def get_queryset(self):
        return PeriodicidadeRecorrencia.objects.all()


class PeriodicidadeRecorrenciaCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = PeriodicidadeRecorrencia
    form_class = PeriodicidadeRecorrenciaForm
    template_name = "financeiro/dominio/form.html"
    success_url = reverse_lazy("financeiro:periodicidade_list")
    modulo = "financeiro"
    acao = "criar"
    extra_context = {"titulo": "Nova Periodicidade"}


class PeriodicidadeRecorrenciaUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = PeriodicidadeRecorrencia
    form_class = PeriodicidadeRecorrenciaForm
    template_name = "financeiro/dominio/form.html"
    success_url = reverse_lazy("financeiro:periodicidade_list")
    modulo = "financeiro"
    acao = "editar"
    extra_context = {"titulo": "Editar Periodicidade"}

    def get_queryset(self):
        return PeriodicidadeRecorrencia.objects.all()


class PeriodicidadeRecorrenciaDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = PeriodicidadeRecorrencia
    template_name = "financeiro/dominio/confirmar_exclusao.html"
    success_url = reverse_lazy("financeiro:periodicidade_list")
    modulo = "financeiro"
    acao = "excluir"

    def get_queryset(self):
        return PeriodicidadeRecorrencia.objects.all()


class TipoEncargoListView(PermissaoModuloMixin, ListView):
    model = TipoEncargo
    template_name = "financeiro/dominio/tipo_encargo_list.html"
    context_object_name = "objetos"
    modulo = "financeiro"
    acao = "ver"

    def get_queryset(self):
        return TipoEncargo.objects.all()


class TipoEncargoCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = TipoEncargo
    form_class = TipoEncargoForm
    template_name = "financeiro/dominio/form.html"
    success_url = reverse_lazy("financeiro:tipo_encargo_list")
    modulo = "financeiro"
    acao = "criar"
    extra_context = {"titulo": "Novo Tipo de Encargo"}


class TipoEncargoUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = TipoEncargo
    form_class = TipoEncargoForm
    template_name = "financeiro/dominio/form.html"
    success_url = reverse_lazy("financeiro:tipo_encargo_list")
    modulo = "financeiro"
    acao = "editar"
    extra_context = {"titulo": "Editar Tipo de Encargo"}

    def get_queryset(self):
        return TipoEncargo.objects.all()


class TipoEncargoDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = TipoEncargo
    template_name = "financeiro/dominio/confirmar_exclusao.html"
    success_url = reverse_lazy("financeiro:tipo_encargo_list")
    modulo = "financeiro"
    acao = "excluir"

    def get_queryset(self):
        return TipoEncargo.objects.all()


class TipoCenarioFluxoListView(PermissaoModuloMixin, ListView):
    model = TipoCenarioFluxo
    template_name = "financeiro/dominio/tipo_cenario_fluxo_list.html"
    context_object_name = "objetos"
    modulo = "financeiro"
    acao = "ver"

    def get_queryset(self):
        return TipoCenarioFluxo.objects.all()


class TipoCenarioFluxoCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = TipoCenarioFluxo
    form_class = TipoCenarioFluxoForm
    template_name = "financeiro/dominio/form.html"
    success_url = reverse_lazy("financeiro:tipo_cenario_fluxo_list")
    modulo = "financeiro"
    acao = "criar"
    extra_context = {"titulo": "Novo Cenário de Fluxo"}


class TipoCenarioFluxoUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = TipoCenarioFluxo
    form_class = TipoCenarioFluxoForm
    template_name = "financeiro/dominio/form.html"
    success_url = reverse_lazy("financeiro:tipo_cenario_fluxo_list")
    modulo = "financeiro"
    acao = "editar"
    extra_context = {"titulo": "Editar Cenário de Fluxo"}

    def get_queryset(self):
        return TipoCenarioFluxo.objects.all()


class TipoCenarioFluxoDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = TipoCenarioFluxo
    template_name = "financeiro/dominio/confirmar_exclusao.html"
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
    template_name = "financeiro/conta_pagar/list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "contas_pagar"
    acao = "ver"

    def get_queryset(self):
        qs = super().get_queryset().select_related("fornecedor", "status", "forma_pagamento")
        status_id = self.request.GET.get("status")
        if status_id:
            qs = qs.filter(status_id=status_id)
        vencimento_de = self.request.GET.get("vencimento_de")
        vencimento_ate = self.request.GET.get("vencimento_ate")
        if vencimento_de:
            qs = qs.filter(data_vencimento__gte=vencimento_de)
        if vencimento_ate:
            qs = qs.filter(data_vencimento__lte=vencimento_ate)
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(descricao__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_list"] = StatusContaPagar.objects.filter(ativo=True)
        return ctx


class ContaPagarDetailView(PermissaoModuloMixin, DetailView):
    model = ContaPagar
    template_name = "financeiro/conta_pagar/detail.html"
    context_object_name = "conta"
    modulo = "contas_pagar"
    acao = "ver"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["encargos"] = self.object.encargos.all()
        ctx["documentos"] = self.object.documentos.all()
        ctx["aprovacoes"] = self.object.historico_aprovacoes.all()
        ctx["parcelas"] = self.object.parcelas.all()
        return ctx


class ContaPagarCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = ContaPagar
    form_class = ContaPagarForm
    template_name = "financeiro/conta_pagar/form.html"
    success_url = reverse_lazy("financeiro:conta_pagar_list")
    modulo = "contas_pagar"
    acao = "criar"
    extra_context = {"titulo": "Nova Conta a Pagar"}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class ContaPagarUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = ContaPagar
    form_class = ContaPagarForm
    template_name = "financeiro/conta_pagar/form.html"
    success_url = reverse_lazy("financeiro:conta_pagar_list")
    modulo = "contas_pagar"
    acao = "editar"
    extra_context = {"titulo": "Editar Conta a Pagar"}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class ContaPagarDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = ContaPagar
    template_name = "financeiro/conta_pagar/confirmar_exclusao.html"
    success_url = reverse_lazy("financeiro:conta_pagar_list")
    modulo = "contas_pagar"
    acao = "excluir"


class EncargoContaPagarCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = EncargoContaPagar
    form_class = EncargoContaPagarForm
    template_name = "financeiro/conta_pagar/encargo_form.html"
    modulo = "contas_pagar"
    acao = "editar"

    def get_success_url(self):
        return reverse_lazy("financeiro:conta_pagar_detail", kwargs={"pk": self.kwargs["conta_pk"]})

    def form_valid(self, form):
        form.instance.conta_pagar = ContaPagar.objects.get(
            pk=self.kwargs["conta_pk"], empresa=self.get_empresa()
        )
        return super().form_valid(form)


class EncargoContaPagarDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = EncargoContaPagar
    template_name = "financeiro/conta_pagar/confirmar_exclusao_encargo.html"
    modulo = "contas_pagar"
    acao = "editar"

    def get_queryset(self):
        return EncargoContaPagar.objects.filter(conta_pagar__empresa=self.get_empresa())

    def get_success_url(self):
        return reverse_lazy("financeiro:conta_pagar_detail", kwargs={"pk": self.object.conta_pagar_id})


class DocumentoContaPagarCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = DocumentoContaPagar
    form_class = DocumentoContaPagarForm
    template_name = "financeiro/conta_pagar/documento_form.html"
    modulo = "contas_pagar"
    acao = "editar"

    def get_success_url(self):
        return reverse_lazy("financeiro:conta_pagar_detail", kwargs={"pk": self.kwargs["conta_pk"]})

    def form_valid(self, form):
        form.instance.conta_pagar = ContaPagar.objects.get(
            pk=self.kwargs["conta_pk"], empresa=self.get_empresa()
        )
        form.instance.enviado_por = self.request.user
        return super().form_valid(form)


class DocumentoContaPagarDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = DocumentoContaPagar
    template_name = "financeiro/conta_pagar/confirmar_exclusao_documento.html"
    modulo = "contas_pagar"
    acao = "editar"

    def get_queryset(self):
        return DocumentoContaPagar.objects.filter(conta_pagar__empresa=self.get_empresa())

    def get_success_url(self):
        return reverse_lazy("financeiro:conta_pagar_detail", kwargs={"pk": self.object.conta_pagar_id})


class AprovacaoContaPagarCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    """Registra aprovação ou rejeição na cadeia multinível."""
    model = AprovacaoContaPagar
    template_name = "financeiro/conta_pagar/aprovacao_form.html"
    fields = ["decisao", "justificativa"]
    modulo = "contas_pagar"
    acao = "criar"

    def get_success_url(self):
        return reverse_lazy("financeiro:conta_pagar_detail", kwargs={"pk": self.kwargs["conta_pk"]})

    def form_valid(self, form):
        conta = ContaPagar.objects.get(pk=self.kwargs["conta_pk"], empresa=self.get_empresa())
        perfil = self.request.user.perfil_acesso
        form.instance.conta_pagar = conta
        form.instance.usuario = self.request.user
        form.instance.nivel_aprovacao = perfil.nivel_aprovacao if perfil else 1
        if form.instance.decisao == "APROVADO":
            conta.aprovado_por = self.request.user
            conta.data_aprovacao = timezone.now()
            conta.save(update_fields=["aprovado_por", "data_aprovacao"])
        return super().form_valid(form)


# ══════════════════════════════════════════════
# CONTAS A RECEBER
# ══════════════════════════════════════════════

class ContaReceberListView(PermissaoModuloMixin, ListView):
    model = ContaReceber
    template_name = "financeiro/conta_receber/list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "contas_receber"
    acao = "ver"

    def get_queryset(self):
        qs = super().get_queryset().select_related("cliente", "status", "forma_pagamento")
        status_id = self.request.GET.get("status")
        if status_id:
            qs = qs.filter(status_id=status_id)
        vencimento_de = self.request.GET.get("vencimento_de")
        vencimento_ate = self.request.GET.get("vencimento_ate")
        if vencimento_de:
            qs = qs.filter(data_vencimento__gte=vencimento_de)
        if vencimento_ate:
            qs = qs.filter(data_vencimento__lte=vencimento_ate)
        inadimplente = self.request.GET.get("inadimplente")
        if inadimplente == "true":
            qs = qs.filter(cliente__inadimplente=True)
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(descricao__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_list"] = StatusContaReceber.objects.filter(ativo=True)
        return ctx


class ContaReceberDetailView(PermissaoModuloMixin, DetailView):
    model = ContaReceber
    template_name = "financeiro/conta_receber/detail.html"
    context_object_name = "conta"
    modulo = "contas_receber"
    acao = "ver"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["encargos"] = self.object.encargos.all()
        ctx["documentos"] = self.object.documentos.all()
        ctx["parcelas"] = self.object.parcelas.all()
        return ctx


class ContaReceberCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = ContaReceber
    form_class = ContaReceberForm
    template_name = "financeiro/conta_receber/form.html"
    success_url = reverse_lazy("financeiro:conta_receber_list")
    modulo = "contas_receber"
    acao = "criar"
    extra_context = {"titulo": "Nova Conta a Receber"}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class ContaReceberUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = ContaReceber
    form_class = ContaReceberForm
    template_name = "financeiro/conta_receber/form.html"
    success_url = reverse_lazy("financeiro:conta_receber_list")
    modulo = "contas_receber"
    acao = "editar"
    extra_context = {"titulo": "Editar Conta a Receber"}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class ContaReceberDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = ContaReceber
    template_name = "financeiro/conta_receber/confirmar_exclusao.html"
    success_url = reverse_lazy("financeiro:conta_receber_list")
    modulo = "contas_receber"
    acao = "excluir"


class EncargoContaReceberCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = EncargoContaReceber
    form_class = EncargoContaReceberForm
    template_name = "financeiro/conta_receber/encargo_form.html"
    modulo = "contas_receber"
    acao = "editar"

    def get_success_url(self):
        return reverse_lazy("financeiro:conta_receber_detail", kwargs={"pk": self.kwargs["conta_pk"]})

    def form_valid(self, form):
        form.instance.conta_receber = ContaReceber.objects.get(
            pk=self.kwargs["conta_pk"], empresa=self.get_empresa()
        )
        return super().form_valid(form)


class EncargoContaReceberDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = EncargoContaReceber
    template_name = "financeiro/conta_receber/confirmar_exclusao_encargo.html"
    modulo = "contas_receber"
    acao = "editar"

    def get_queryset(self):
        return EncargoContaReceber.objects.filter(conta_receber__empresa=self.get_empresa())

    def get_success_url(self):
        return reverse_lazy("financeiro:conta_receber_detail", kwargs={"pk": self.object.conta_receber_id})


class DocumentoContaReceberCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = DocumentoContaReceber
    form_class = DocumentoContaReceberForm
    template_name = "financeiro/conta_receber/documento_form.html"
    modulo = "contas_receber"
    acao = "editar"

    def get_success_url(self):
        return reverse_lazy("financeiro:conta_receber_detail", kwargs={"pk": self.kwargs["conta_pk"]})

    def form_valid(self, form):
        form.instance.conta_receber = ContaReceber.objects.get(
            pk=self.kwargs["conta_pk"], empresa=self.get_empresa()
        )
        form.instance.enviado_por = self.request.user
        return super().form_valid(form)


class DocumentoContaReceberDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = DocumentoContaReceber
    template_name = "financeiro/conta_receber/confirmar_exclusao_documento.html"
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
    template_name = "financeiro/lancamento/list.html"
    context_object_name = "objetos"
    paginate_by = 50
    modulo = "fluxo_caixa"
    acao = "ver"

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            "conta_bancaria", "tipo_lancamento", "plano_contas", "centro_custo"
        )
        conta_id = self.request.GET.get("conta_bancaria")
        if conta_id:
            qs = qs.filter(conta_bancaria_id=conta_id)
        data_de = self.request.GET.get("data_de")
        data_ate = self.request.GET.get("data_ate")
        if data_de:
            qs = qs.filter(data_lancamento__gte=data_de)
        if data_ate:
            qs = qs.filter(data_lancamento__lte=data_ate)
        conciliado = self.request.GET.get("conciliado")
        if conciliado in ("true", "false"):
            qs = qs.filter(conciliado=conciliado == "true")
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["contas_bancarias"] = ContaBancaria.objects.filter(empresa=self.get_empresa(), ativo=True)
        return ctx


class LancamentoFinanceiroCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = LancamentoFinanceiro
    form_class = LancamentoFinanceiroForm
    template_name = "financeiro/lancamento/form.html"
    success_url = reverse_lazy("financeiro:lancamento_list")
    modulo = "fluxo_caixa"
    acao = "criar"
    extra_context = {"titulo": "Novo Lançamento"}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class LancamentoFinanceiroUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = LancamentoFinanceiro
    form_class = LancamentoFinanceiroForm
    template_name = "financeiro/lancamento/form.html"
    success_url = reverse_lazy("financeiro:lancamento_list")
    modulo = "fluxo_caixa"
    acao = "editar"
    extra_context = {"titulo": "Editar Lançamento"}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class LancamentoFinanceiroDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = LancamentoFinanceiro
    template_name = "financeiro/lancamento/confirmar_exclusao.html"
    success_url = reverse_lazy("financeiro:lancamento_list")
    modulo = "fluxo_caixa"
    acao = "excluir"


# ══════════════════════════════════════════════
# TRANSFERÊNCIAS BANCÁRIAS
# ══════════════════════════════════════════════

class TransferenciaBancariaListView(PermissaoModuloMixin, ListView):
    model = TransferenciaBancaria
    template_name = "financeiro/transferencia/list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "fluxo_caixa"
    acao = "ver"

    def get_queryset(self):
        return super().get_queryset().select_related("conta_origem", "conta_destino")


class TransferenciaBancariaCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = TransferenciaBancaria
    form_class = TransferenciaBancariaForm
    template_name = "financeiro/transferencia/form.html"
    success_url = reverse_lazy("financeiro:transferencia_list")
    modulo = "fluxo_caixa"
    acao = "criar"
    extra_context = {"titulo": "Nova Transferência Bancária"}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class TransferenciaBancariaDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = TransferenciaBancaria
    template_name = "financeiro/transferencia/confirmar_exclusao.html"
    success_url = reverse_lazy("financeiro:transferencia_list")
    modulo = "fluxo_caixa"
    acao = "excluir"


# ══════════════════════════════════════════════
# PROJEÇÃO DE FLUXO DE CAIXA
# ══════════════════════════════════════════════

class ProjecaoFluxoCaixaListView(PermissaoModuloMixin, ListView):
    model = ProjecaoFluxoCaixa
    template_name = "financeiro/projecao/list.html"
    context_object_name = "objetos"
    modulo = "fluxo_caixa"
    acao = "ver"

    def get_queryset(self):
        return super().get_queryset().select_related("cenario", "conta_bancaria")


class ProjecaoFluxoCaixaCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = ProjecaoFluxoCaixa
    fields = ["conta_bancaria", "cenario", "data_referencia",
              "entradas_previstas", "saidas_previstas", "saldo_projetado"]
    template_name = "financeiro/projecao/form.html"
    success_url = reverse_lazy("financeiro:projecao_list")
    modulo = "fluxo_caixa"
    acao = "criar"
    extra_context = {"titulo": "Nova Projeção"}


class ProjecaoFluxoCaixaDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = ProjecaoFluxoCaixa
    template_name = "financeiro/projecao/confirmar_exclusao.html"
    success_url = reverse_lazy("financeiro:projecao_list")
    modulo = "fluxo_caixa"
    acao = "excluir"