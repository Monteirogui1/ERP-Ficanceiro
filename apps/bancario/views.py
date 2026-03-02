from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from apps.authentication.mixins import PermissaoModuloMixin
from .models import (
    TipoArquivoBancario, StatusConciliacao, TipoMovimentoBancario,
    ImportacaoExtrato, ConciliacaoBancaria, DivergenciaConciliacao,
    ArquivoRemessa, ArquivoRetorno,
)
from .forms import (
    TipoArquivoBancarioForm, StatusConciliacaoForm, TipoMovimentoBancarioForm,
    ImportacaoExtratoForm, ConciliacaoBancariaForm,
    ArquivoRemessaForm, ArquivoRetornoForm,
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

class TipoArquivoBancarioListView(PermissaoModuloMixin, ListView):
    model = TipoArquivoBancario
    template_name = "bancario/dominio/tipo_arquivo_list.html"
    context_object_name = "objetos"
    modulo = "bancario"
    acao = "ver"

    def get_queryset(self):
        return TipoArquivoBancario.objects.all()


class TipoArquivoBancarioCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = TipoArquivoBancario
    form_class = TipoArquivoBancarioForm
    template_name = "bancario/dominio/form.html"
    success_url = reverse_lazy("bancario:tipo_arquivo_list")
    modulo = "bancario"
    acao = "criar"
    extra_context = {"titulo": "Novo Tipo de Arquivo Bancário"}


class TipoArquivoBancarioUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = TipoArquivoBancario
    form_class = TipoArquivoBancarioForm
    template_name = "bancario/dominio/form.html"
    success_url = reverse_lazy("bancario:tipo_arquivo_list")
    modulo = "bancario"
    acao = "editar"
    extra_context = {"titulo": "Editar Tipo de Arquivo Bancário"}

    def get_queryset(self):
        return TipoArquivoBancario.objects.all()


class TipoArquivoBancarioDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = TipoArquivoBancario
    template_name = "bancario/dominio/confirmar_exclusao.html"
    success_url = reverse_lazy("bancario:tipo_arquivo_list")
    modulo = "bancario"
    acao = "excluir"

    def get_queryset(self):
        return TipoArquivoBancario.objects.all()


class StatusConciliacaoListView(PermissaoModuloMixin, ListView):
    model = StatusConciliacao
    template_name = "bancario/dominio/status_conciliacao_list.html"
    context_object_name = "objetos"
    modulo = "bancario"
    acao = "ver"

    def get_queryset(self):
        return StatusConciliacao.objects.all()


class StatusConciliacaoCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = StatusConciliacao
    form_class = StatusConciliacaoForm
    template_name = "bancario/dominio/form.html"
    success_url = reverse_lazy("bancario:status_conciliacao_list")
    modulo = "bancario"
    acao = "criar"
    extra_context = {"titulo": "Novo Status de Conciliação"}


class StatusConciliacaoUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = StatusConciliacao
    form_class = StatusConciliacaoForm
    template_name = "bancario/dominio/form.html"
    success_url = reverse_lazy("bancario:status_conciliacao_list")
    modulo = "bancario"
    acao = "editar"
    extra_context = {"titulo": "Editar Status de Conciliação"}

    def get_queryset(self):
        return StatusConciliacao.objects.all()


class StatusConciliacaoDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = StatusConciliacao
    template_name = "bancario/dominio/confirmar_exclusao.html"
    success_url = reverse_lazy("bancario:status_conciliacao_list")
    modulo = "bancario"
    acao = "excluir"

    def get_queryset(self):
        return StatusConciliacao.objects.all()


class TipoMovimentoBancarioListView(PermissaoModuloMixin, ListView):
    model = TipoMovimentoBancario
    template_name = "bancario/dominio/tipo_movimento_list.html"
    context_object_name = "objetos"
    modulo = "bancario"
    acao = "ver"

    def get_queryset(self):
        return TipoMovimentoBancario.objects.all()


class TipoMovimentoBancarioCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = TipoMovimentoBancario
    form_class = TipoMovimentoBancarioForm
    template_name = "bancario/dominio/form.html"
    success_url = reverse_lazy("bancario:tipo_movimento_list")
    modulo = "bancario"
    acao = "criar"
    extra_context = {"titulo": "Novo Tipo de Movimento Bancário"}


class TipoMovimentoBancarioUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = TipoMovimentoBancario
    form_class = TipoMovimentoBancarioForm
    template_name = "bancario/dominio/form.html"
    success_url = reverse_lazy("bancario:tipo_movimento_list")
    modulo = "bancario"
    acao = "editar"
    extra_context = {"titulo": "Editar Tipo de Movimento Bancário"}

    def get_queryset(self):
        return TipoMovimentoBancario.objects.all()


class TipoMovimentoBancarioDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = TipoMovimentoBancario
    template_name = "bancario/dominio/confirmar_exclusao.html"
    success_url = reverse_lazy("bancario:tipo_movimento_list")
    modulo = "bancario"
    acao = "excluir"

    def get_queryset(self):
        return TipoMovimentoBancario.objects.all()


# ══════════════════════════════════════════════
# EXTRATOS E MOVIMENTOS
# ══════════════════════════════════════════════

class ImportacaoExtratoListView(PermissaoModuloMixin, ListView):
    model = ImportacaoExtrato
    template_name = "bancario/extrato/list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "bancario"
    acao = "ver"

    def get_queryset(self):
        return super().get_queryset().select_related("conta_bancaria", "tipo_arquivo")


class ImportacaoExtratoCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = ImportacaoExtrato
    form_class = ImportacaoExtratoForm
    template_name = "bancario/extrato/form.html"
    success_url = reverse_lazy("bancario:importacao_list")
    modulo = "bancario"
    acao = "criar"
    extra_context = {"titulo": "Importar Extrato Bancário"}

    def form_valid(self, form):
        form.instance.importado_por = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class ImportacaoExtratoDetailView(PermissaoModuloMixin, DetailView):
    model = ImportacaoExtrato
    template_name = "bancario/extrato/detail.html"
    context_object_name = "importacao"
    modulo = "bancario"
    acao = "ver"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["movimentos"] = self.object.movimentos.select_related(
            "tipo_movimento", "status_conciliacao"
        ).all()
        return ctx


# ══════════════════════════════════════════════
# CONCILIAÇÃO BANCÁRIA
# ══════════════════════════════════════════════

class ConciliacaoBancariaListView(PermissaoModuloMixin, ListView):
    model = ConciliacaoBancaria
    template_name = "bancario/conciliacao/list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "bancario"
    acao = "ver"

    def get_queryset(self):
        return super().get_queryset().select_related(
            "movimento_bancario", "lancamento", "status"
        )


class ConciliacaoBancariaCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = ConciliacaoBancaria
    form_class = ConciliacaoBancariaForm
    template_name = "bancario/conciliacao/form.html"
    success_url = reverse_lazy("bancario:conciliacao_list")
    modulo = "bancario"
    acao = "criar"
    extra_context = {"titulo": "Nova Conciliação Manual"}

    def form_valid(self, form):
        form.instance.conciliado_por = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class ConciliacaoBancariaDeleteView(MensagemSucessoMixin, PermissaoModuloMixin, DeleteView):
    model = ConciliacaoBancaria
    template_name = "bancario/conciliacao/confirmar_exclusao.html"
    success_url = reverse_lazy("bancario:conciliacao_list")
    modulo = "bancario"
    acao = "excluir"


class DivergenciaConciliacaoListView(PermissaoModuloMixin, ListView):
    model = DivergenciaConciliacao
    template_name = "bancario/divergencia/list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "bancario"
    acao = "ver"

    def get_queryset(self):
        qs = super().get_queryset().select_related("movimento_bancario", "lancamento")
        resolvida = self.request.GET.get("resolvida")
        if resolvida in ("true", "false"):
            qs = qs.filter(resolvida=resolvida == "true")
        return qs


class DivergenciaConciliacaoUpdateView(MensagemSucessoMixin, PermissaoModuloMixin, UpdateView):
    model = DivergenciaConciliacao
    fields = ["resolvida", "resolucao"]
    template_name = "bancario/divergencia/form.html"
    success_url = reverse_lazy("bancario:divergencia_list")
    modulo = "bancario"
    acao = "editar"
    extra_context = {"titulo": "Resolver Divergência"}


# ══════════════════════════════════════════════
# REMESSA E RETORNO
# ══════════════════════════════════════════════

class ArquivoRemessaListView(PermissaoModuloMixin, ListView):
    model = ArquivoRemessa
    template_name = "bancario/remessa/list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "bancario"
    acao = "ver"

    def get_queryset(self):
        return super().get_queryset().select_related("conta_bancaria")


class ArquivoRemessaCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = ArquivoRemessa
    form_class = ArquivoRemessaForm
    template_name = "bancario/remessa/form.html"
    success_url = reverse_lazy("bancario:remessa_list")
    modulo = "bancario"
    acao = "criar"
    extra_context = {"titulo": "Gerar Arquivo de Remessa"}

    def form_valid(self, form):
        form.instance.gerado_por = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class ArquivoRetornoListView(PermissaoModuloMixin, ListView):
    model = ArquivoRetorno
    template_name = "bancario/retorno/list.html"
    context_object_name = "objetos"
    paginate_by = 25
    modulo = "bancario"
    acao = "ver"

    def get_queryset(self):
        return super().get_queryset().select_related("conta_bancaria", "arquivo_remessa")


class ArquivoRetornoCreateView(MensagemSucessoMixin, PermissaoModuloMixin, CreateView):
    model = ArquivoRetorno
    form_class = ArquivoRetornoForm
    template_name = "bancario/retorno/form.html"
    success_url = reverse_lazy("bancario:retorno_list")
    modulo = "bancario"
    acao = "criar"
    extra_context = {"titulo": "Importar Arquivo de Retorno"}

    def form_valid(self, form):
        form.instance.importado_por = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs