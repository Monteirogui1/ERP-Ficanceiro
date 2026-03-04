from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from apps.authentication.mixins import PermissaoModuloMixin
from .models import (
    TipoArquivoBancario, StatusConciliacao, TipoMovimentoBancario,
    ImportacaoExtrato, MovimentoBancario,
    ConciliacaoBancaria, DivergenciaConciliacao,
    ArquivoRemessa, ArquivoRetorno,
)
from .forms import (
    TipoArquivoBancarioForm, StatusConciliacaoForm, TipoMovimentoBancarioForm,
    ImportacaoExtratoForm,
    ConciliacaoBancariaForm,
    ArquivoRemessaForm, ArquivoRetornoForm,
)
from .services.conciliacao_automatica import ConciliacaoAutomaticaService


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

class TipoArquivoBancarioListView(PermissaoModuloMixin, ListView):
    model = TipoArquivoBancario
    template_name = "bancario/dominio_list.html"
    context_object_name = "objetos"
    modulo = "bancario"
    acao = "ver"
    extra_context = {
        "titulo": "Tipos de Arquivo Bancário",
        "create_url": "bancario:tipo_arquivo_create",
        "update_url": "bancario:tipo_arquivo_update",
        "delete_url": "bancario:tipo_arquivo_delete",
    }

    def get_queryset(self):
        return TipoArquivoBancario.objects.all().order_by("nome")


class TipoArquivoBancarioCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = TipoArquivoBancario
    form_class = TipoArquivoBancarioForm
    template_name = "bancario/dominio_form.html"
    success_url = reverse_lazy("bancario:tipo_arquivo_list")
    modulo = "bancario"
    acao = "criar"
    extra_context = {"titulo": "Novo Tipo de Arquivo", "list_url": "bancario:tipo_arquivo_list"}


class TipoArquivoBancarioUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = TipoArquivoBancario
    form_class = TipoArquivoBancarioForm
    template_name = "bancario/dominio_form.html"
    success_url = reverse_lazy("bancario:tipo_arquivo_list")
    modulo = "bancario"
    acao = "editar"
    extra_context = {"titulo": "Editar Tipo de Arquivo", "list_url": "bancario:tipo_arquivo_list"}

    def get_queryset(self):
        return TipoArquivoBancario.objects.all()


class TipoArquivoBancarioDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = TipoArquivoBancario
    template_name = "bancario/dominio_confirmar_exclusao.html"
    success_url = reverse_lazy("bancario:tipo_arquivo_list")
    modulo = "bancario"
    acao = "excluir"

    def get_queryset(self):
        return TipoArquivoBancario.objects.all()


class StatusConciliacaoListView(PermissaoModuloMixin, ListView):
    model = StatusConciliacao
    template_name = "bancario/dominio_list.html"
    context_object_name = "objetos"
    modulo = "bancario"
    acao = "ver"
    extra_context = {
        "titulo": "Status de Conciliação",
        "create_url": "bancario:status_conciliacao_create",
        "update_url": "bancario:status_conciliacao_update",
        "delete_url": "bancario:status_conciliacao_delete",
    }

    def get_queryset(self):
        return StatusConciliacao.objects.all().order_by("nome")


class StatusConciliacaoCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = StatusConciliacao
    form_class = StatusConciliacaoForm
    template_name = "bancario/dominio_form.html"
    success_url = reverse_lazy("bancario:status_conciliacao_list")
    modulo = "bancario"
    acao = "criar"
    extra_context = {"titulo": "Novo Status de Conciliação", "list_url": "bancario:status_conciliacao_list"}


class StatusConciliacaoUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = StatusConciliacao
    form_class = StatusConciliacaoForm
    template_name = "bancario/dominio_form.html"
    success_url = reverse_lazy("bancario:status_conciliacao_list")
    modulo = "bancario"
    acao = "editar"
    extra_context = {"titulo": "Editar Status de Conciliação", "list_url": "bancario:status_conciliacao_list"}

    def get_queryset(self):
        return StatusConciliacao.objects.all()


class StatusConciliacaoDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = StatusConciliacao
    template_name = "bancario/dominio_confirmar_exclusao.html"
    success_url = reverse_lazy("bancario:status_conciliacao_list")
    modulo = "bancario"
    acao = "excluir"

    def get_queryset(self):
        return StatusConciliacao.objects.all()


class TipoMovimentoBancarioListView(PermissaoModuloMixin, ListView):
    model = TipoMovimentoBancario
    template_name = "bancario/dominio_list.html"
    context_object_name = "objetos"
    modulo = "bancario"
    acao = "ver"
    extra_context = {
        "titulo": "Tipos de Movimento Bancário",
        "create_url": "bancario:tipo_movimento_create",
        "update_url": "bancario:tipo_movimento_update",
        "delete_url": "bancario:tipo_movimento_delete",
    }

    def get_queryset(self):
        return TipoMovimentoBancario.objects.all().order_by("nome")


class TipoMovimentoBancarioCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = TipoMovimentoBancario
    form_class = TipoMovimentoBancarioForm
    template_name = "bancario/dominio_form.html"
    success_url = reverse_lazy("bancario:tipo_movimento_list")
    modulo = "bancario"
    acao = "criar"
    extra_context = {"titulo": "Novo Tipo de Movimento", "list_url": "bancario:tipo_movimento_list"}


class TipoMovimentoBancarioUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = TipoMovimentoBancario
    form_class = TipoMovimentoBancarioForm
    template_name = "bancario/dominio_form.html"
    success_url = reverse_lazy("bancario:tipo_movimento_list")
    modulo = "bancario"
    acao = "editar"
    extra_context = {"titulo": "Editar Tipo de Movimento", "list_url": "bancario:tipo_movimento_list"}

    def get_queryset(self):
        return TipoMovimentoBancario.objects.all()


class TipoMovimentoBancarioDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = TipoMovimentoBancario
    template_name = "bancario/dominio_confirmar_exclusao.html"
    success_url = reverse_lazy("bancario:tipo_movimento_list")
    modulo = "bancario"
    acao = "excluir"

    def get_queryset(self):
        return TipoMovimentoBancario.objects.all()


# ══════════════════════════════════════════════
# IMPORTAÇÃO DE EXTRATO
# ══════════════════════════════════════════════

class ImportacaoExtratoListView(PermissaoModuloMixin, ListView):
    model = ImportacaoExtrato
    template_name = "bancario/extrato_list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "bancario"
    acao = "ver"

    def get_queryset(self):
        return (
            super().get_queryset()
            .select_related("conta_bancaria", "tipo_arquivo")
            .order_by("-criado_em")
        )


class ImportacaoExtratoCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = ImportacaoExtrato
    form_class = ImportacaoExtratoForm
    template_name = "bancario/extrato_form.html"
    success_url = reverse_lazy("bancario:importacao_list")
    modulo = "bancario"
    acao = "criar"
    extra_context = {"titulo": "Importar Extrato Bancário"}

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def form_valid(self, form):
        form.instance.empresa      = self.get_empresa()
        form.instance.importado_por = self.request.user
        if form.instance.arquivo:
            form.instance.nome_arquivo = form.instance.arquivo.name.split("/")[-1]
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("bancario:importacao_detail", kwargs={"pk": self.object.pk})


class ImportacaoExtratoDetailView(PermissaoModuloMixin, DetailView):
    model = ImportacaoExtrato
    template_name = "bancario/extrato_detail.html"
    context_object_name = "importacao"
    modulo = "bancario"
    acao = "ver"

    def get_queryset(self):
        return ImportacaoExtrato.objects.filter(empresa=self.get_empresa())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["movimentos"] = (
            self.object.movimentos
            .select_related("tipo_movimento", "status_conciliacao")
            .order_by("data_movimento")
        )
        return ctx


# ══════════════════════════════════════════════
# CONCILIAÇÃO BANCÁRIA
# ══════════════════════════════════════════════

class ConciliacaoBancariaListView(PermissaoModuloMixin, ListView):
    model = ConciliacaoBancaria
    template_name = "bancario/conciliacao_list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "bancario"
    acao = "ver"

    def get_queryset(self):
        qs = (
            super().get_queryset()
            .select_related(
                "movimento_bancario__conta_bancaria",
                "lancamento",
                "status",
                "conciliado_por",
            )
            .order_by("-criado_em")
        )
        if status_id := self.request.GET.get("status"):
            qs = qs.filter(status_id=status_id)
        if automatica := self.request.GET.get("automatica"):
            if automatica in ("true", "false"):
                qs = qs.filter(automatica=(automatica == "true"))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_list"] = StatusConciliacao.objects.filter(ativo=True)
        return ctx


class ConciliacaoBancariaCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = ConciliacaoBancaria
    form_class = ConciliacaoBancariaForm
    template_name = "bancario/conciliacao_form.html"
    success_url = reverse_lazy("bancario:conciliacao_list")
    modulo = "bancario"
    acao = "criar"
    extra_context = {"titulo": "Nova Conciliação Manual"}

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def form_valid(self, form):
        form.instance.empresa       = self.get_empresa()
        form.instance.conciliado_por = self.request.user
        return super().form_valid(form)


class ConciliacaoBancariaDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = ConciliacaoBancaria
    template_name = "bancario/conciliacao_confirmar_exclusao.html"
    success_url = reverse_lazy("bancario:conciliacao_list")
    modulo = "bancario"
    acao = "excluir"

    def get_queryset(self):
        return ConciliacaoBancaria.objects.filter(empresa=self.get_empresa())


# ══════════════════════════════════════════════
# DIVERGÊNCIAS DE CONCILIAÇÃO
# ══════════════════════════════════════════════

class DivergenciaConciliacaoListView(PermissaoModuloMixin, ListView):
    model = DivergenciaConciliacao
    template_name = "bancario/divergencia_list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "bancario"
    acao = "ver"

    def get_queryset(self):
        qs = (
            super().get_queryset()
            .select_related(
                "movimento_bancario__conta_bancaria",
                "lancamento",
            )
            .filter(empresa=self.get_empresa())
            .order_by("resolvida", "-criado_em")
        )
        if resolvida := self.request.GET.get("resolvida"):
            if resolvida in ("true", "false"):
                qs = qs.filter(resolvida=(resolvida == "true"))
        if tipo := self.request.GET.get("tipo"):
            qs = qs.filter(tipo_divergencia=tipo)
        return qs


class DivergenciaConciliacaoUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = DivergenciaConciliacao
    fields = ["resolvida", "resolucao"]
    template_name = "bancario/divergencia_form.html"
    success_url = reverse_lazy("bancario:divergencia_list")
    modulo = "bancario"
    acao = "editar"
    extra_context = {"titulo": "Resolver Divergência"}

    def get_queryset(self):
        return DivergenciaConciliacao.objects.filter(empresa=self.get_empresa())


# ══════════════════════════════════════════════
# REMESSA E RETORNO
# ══════════════════════════════════════════════

class ArquivoRemessaListView(PermissaoModuloMixin, ListView):
    model = ArquivoRemessa
    template_name = "bancario/remessa_list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "bancario"
    acao = "ver"

    def get_queryset(self):
        return (
            super().get_queryset()
            .select_related("conta_bancaria", "gerado_por")
            .filter(empresa=self.get_empresa())
            .order_by("-criado_em")
        )


class ArquivoRemessaCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = ArquivoRemessa
    form_class = ArquivoRemessaForm
    template_name = "bancario/remessa_form.html"
    success_url = reverse_lazy("bancario:remessa_list")
    modulo = "bancario"
    acao = "criar"
    extra_context = {"titulo": "Gerar Arquivo de Remessa"}

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def form_valid(self, form):
        form.instance.empresa    = self.get_empresa()
        form.instance.gerado_por = self.request.user
        return super().form_valid(form)


class ArquivoRetornoListView(PermissaoModuloMixin, ListView):
    model = ArquivoRetorno
    template_name = "bancario/retorno_list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "bancario"
    acao = "ver"

    def get_queryset(self):
        return (
            super().get_queryset()
            .select_related("conta_bancaria", "arquivo_remessa", "importado_por")
            .filter(empresa=self.get_empresa())
            .order_by("-criado_em")
        )


class ArquivoRetornoCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = ArquivoRetorno
    form_class = ArquivoRetornoForm
    template_name = "bancario/retorno_form.html"
    success_url = reverse_lazy("bancario:retorno_list")
    modulo = "bancario"
    acao = "criar"
    extra_context = {"titulo": "Importar Arquivo de Retorno"}

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["empresa"] = self.get_empresa()
        return kw

    def form_valid(self, form):
        form.instance.empresa      = self.get_empresa()
        form.instance.importado_por = self.request.user
        if form.instance.arquivo:
            form.instance.nome_arquivo = form.instance.arquivo.name.split("/")[-1]
        return super().form_valid(form)



class ConciliarAutomaticoView(PermissaoModuloMixin, View):
    modulo = "bancario"
    acao = "editar"

    def post(self, request, pk):
        importacao = get_object_or_404(ImportacaoExtrato, pk=pk, empresa=self.get_empresa())
        svc = ConciliacaoAutomaticaService(importacao, usuario=request.user)
        resultado = svc.executar()
        messages.success(
            request,
            f"Conciliação concluída: {resultado['conciliados']} conciliados, "
            f"{resultado['divergentes']} divergentes."
        )
        return redirect("bancario:importacao_detail", pk=pk)