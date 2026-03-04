from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView,
    TemplateView,
)

from .forms import (
    EmpresaForm, FilialEmpresaForm,
    PerfilAcessoForm, UsuarioForm, UsuarioEdicaoForm,
    SegmentoEmpresaForm, RegimeTributarioForm,
    TipoDocumentoForm, TipoContatoForm,
    TipoAcaoLogForm, TipoNotificacaoForm,
)
from .models import (
    Empresa, FilialEmpresa,
    PerfilAcesso, Usuario, UsuarioEmpresa,
    LogAuditoria, Notificacao,
    SegmentoEmpresa, RegimeTributario,
    TipoDocumento, TipoContato,
    TipoAcaoLog, TipoNotificacao,
)


# ══════════════════════════════════════════════
# MIXINS
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


class SuperuserRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_superuser:
            raise PermissionDenied("Apenas superusuários podem acessar esta área.")
        return super().dispatch(request, *args, **kwargs)


class EmpresaSessionMixin(LoginRequiredMixin):
    """
    Disponibiliza get_empresa() resolvido pela sessão.
    Redireciona para seleção de empresa se nenhuma estiver ativa.
    """

    def get_empresa(self):
        empresa_id = self.request.session.get("empresa_ativa_id")
        if not empresa_id:
            return None
        try:
            ue = self.request.user.empresas_acesso.select_related("empresa").get(
                empresa_id=empresa_id, ativo=True
            )
            return ue.empresa
        except UsuarioEmpresa.DoesNotExist:
            return None

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.user.is_authenticated and not request.user.is_superuser:
            if not self.get_empresa():
                messages.warning(request, "Selecione uma empresa para continuar.")
                return redirect("authentication:selecionar_empresa")
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["empresa_ativa"] = self.get_empresa()
        return ctx


# ══════════════════════════════════════════════
# SELEÇÃO DE EMPRESA
# ══════════════════════════════════════════════

class SelecionarEmpresaView(LoginRequiredMixin, TemplateView):
    template_name = "authentication/selecionar_empresa.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["empresas_usuario"] = (
            UsuarioEmpresa.objects
            .filter(usuario=self.request.user, ativo=True)
            .select_related("empresa")
            .order_by("empresa__razao_social")
        )
        ctx["empresa_ativa_id"] = self.request.session.get("empresa_ativa_id")
        return ctx

    def post(self, request, *args, **kwargs):
        empresa_id = request.POST.get("empresa_id")
        if not empresa_id:
            messages.error(request, "Selecione uma empresa.")
            return self.get(request, *args, **kwargs)

        ue = UsuarioEmpresa.objects.filter(
            usuario=request.user,
            empresa_id=empresa_id,
            ativo=True,
        ).first()
        if not ue:
            messages.error(request, "Você não tem acesso a esta empresa.")
            return self.get(request, *args, **kwargs)

        request.session["empresa_ativa_id"] = int(empresa_id)
        messages.success(request, f"Empresa '{ue.empresa.razao_social}' selecionada.")
        return redirect(request.GET.get("next", "authentication:dashboard"))


# ══════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════

class DashboardView(EmpresaSessionMixin, TemplateView):
    template_name = "authentication/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empresa = self.get_empresa()
        today = timezone.localdate()
        ctx["today"] = today

        if empresa:
            from apps.financeiro.models import ContaPagar, ContaReceber
            from apps.fiscal.models import ObrigacaoFiscal
            from apps.bancario.models import DivergenciaConciliacao

            proximos_30 = today + timezone.timedelta(days=30)

            ctx["total_pagar"] = ContaPagar.objects.filter(
                empresa=empresa,
                data_pagamento__isnull=True,
                data_vencimento__lte=proximos_30,
            ).count()

            ctx["total_receber"] = ContaReceber.objects.filter(
                empresa=empresa,
                data_recebimento__isnull=True,
                data_vencimento__lte=proximos_30,
            ).count()

            ctx["total_obrigacoes"] = ObrigacaoFiscal.objects.filter(
                empresa=empresa,
                data_entrega__isnull=True,
                data_vencimento__lte=proximos_30,
            ).count()

            ctx["total_divergencias"] = DivergenciaConciliacao.objects.filter(
                empresa=empresa,
                resolvida=False,
            ).count()

            ctx["ultimas_pagar"] = (
                ContaPagar.objects
                .filter(empresa=empresa, data_pagamento__isnull=True)
                .select_related("fornecedor", "status")
                .order_by("data_vencimento")[:8]
            )

            ctx["proximas_obrigacoes"] = (
                ObrigacaoFiscal.objects
                .filter(empresa=empresa, data_entrega__isnull=True)
                .select_related("tipo", "status")
                .order_by("data_vencimento")[:8]
            )

            ctx["notificacoes"] = (
                Notificacao.objects
                .filter(usuario=self.request.user, lida=False)
                .order_by("-criado_em")[:5]
            )

        return ctx


# ══════════════════════════════════════════════
# EMPRESAS  (somente superusuário)
# ══════════════════════════════════════════════

class EmpresaListView(SuperuserRequiredMixin, ListView):
    model = Empresa
    template_name = "authentication/empresa_list.html"
    context_object_name = "objetos"
    paginate_by = 25

    def get_queryset(self):
        qs = Empresa.objects.all().order_by("razao_social")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(razao_social__icontains=q)
        return qs


class EmpresaCreateView(MensagemSucessoMixin, SuperuserRequiredMixin, CreateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = "authentication/empresa_form.html"
    success_url = reverse_lazy("authentication:empresa_list")
    extra_context = {"titulo": "Nova Empresa"}


class EmpresaUpdateView(MensagemSucessoMixin, SuperuserRequiredMixin, UpdateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = "authentication/empresa_form.html"
    success_url = reverse_lazy("authentication:empresa_list")
    extra_context = {"titulo": "Editar Empresa"}


class EmpresaDeleteView(MensagemSucessoMixin, SuperuserRequiredMixin, DeleteView):
    model = Empresa
    template_name = "authentication/confirmar_exclusao.html"
    success_url = reverse_lazy("authentication:empresa_list")


# ══════════════════════════════════════════════
# FILIAIS
# ══════════════════════════════════════════════

class FilialListView(SuperuserRequiredMixin, ListView):
    model = FilialEmpresa
    template_name = "authentication/filial_list.html"
    context_object_name = "objetos"

    def _get_empresa_obj(self):
        return get_object_or_404(Empresa, pk=self.kwargs["empresa_pk"])

    def get_queryset(self):
        return FilialEmpresa.objects.filter(
            empresa_id=self.kwargs["empresa_pk"]
        ).order_by("nome")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["empresa_mae"] = self._get_empresa_obj()
        return ctx


class FilialCreateView(MensagemSucessoMixin, SuperuserRequiredMixin, CreateView):
    model = FilialEmpresa
    form_class = FilialEmpresaForm
    template_name = "authentication/filial_form.html"
    extra_context = {"titulo": "Nova Filial"}

    def get_success_url(self):
        return reverse_lazy("authentication:filial_list", kwargs={"empresa_pk": self.kwargs["empresa_pk"]})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = get_object_or_404(Empresa, pk=self.kwargs["empresa_pk"])
        return kwargs

    def form_valid(self, form):
        form.instance.empresa = get_object_or_404(Empresa, pk=self.kwargs["empresa_pk"])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["empresa_mae"] = get_object_or_404(Empresa, pk=self.kwargs["empresa_pk"])
        return ctx


class FilialUpdateView(MensagemSucessoMixin, SuperuserRequiredMixin, UpdateView):
    model = FilialEmpresa
    form_class = FilialEmpresaForm
    template_name = "authentication/filial_form.html"
    extra_context = {"titulo": "Editar Filial"}

    def get_success_url(self):
        return reverse_lazy("authentication:filial_list", kwargs={"empresa_pk": self.object.empresa_id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.object.empresa
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["empresa_mae"] = self.object.empresa
        return ctx


class FilialDeleteView(MensagemSucessoMixin, SuperuserRequiredMixin, DeleteView):
    model = FilialEmpresa
    template_name = "authentication/confirmar_exclusao.html"

    def get_success_url(self):
        return reverse_lazy("authentication:filial_list", kwargs={"empresa_pk": self.object.empresa_id})


# ══════════════════════════════════════════════
# PERFIS DE ACESSO
# ══════════════════════════════════════════════

class PerfilAcessoListView(EmpresaSessionMixin, ListView):
    model = PerfilAcesso
    template_name = "authentication/perfil_list.html"
    context_object_name = "objetos"
    paginate_by = 25

    def get_queryset(self):
        empresa = self.get_empresa()
        if not empresa:
            return PerfilAcesso.objects.none()
        return PerfilAcesso.objects.filter(empresa=empresa).order_by("nome")


class PerfilAcessoCreateView(MensagemSucessoMixin, EmpresaSessionMixin, CreateView):
    model = PerfilAcesso
    form_class = PerfilAcessoForm
    template_name = "authentication/perfil_form.html"
    success_url = reverse_lazy("authentication:perfil_list")
    extra_context = {"titulo": "Novo Perfil de Acesso"}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        return super().form_valid(form)


class PerfilAcessoUpdateView(MensagemSucessoMixin, EmpresaSessionMixin, UpdateView):
    model = PerfilAcesso
    form_class = PerfilAcessoForm
    template_name = "authentication/perfil_form.html"
    success_url = reverse_lazy("authentication:perfil_list")
    extra_context = {"titulo": "Editar Perfil de Acesso"}

    def get_queryset(self):
        empresa = self.get_empresa()
        if not empresa:
            return PerfilAcesso.objects.none()
        return PerfilAcesso.objects.filter(empresa=empresa)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class PerfilAcessoDeleteView(MensagemSucessoMixin, EmpresaSessionMixin, DeleteView):
    model = PerfilAcesso
    template_name = "authentication/confirmar_exclusao.html"
    success_url = reverse_lazy("authentication:perfil_list")

    def get_queryset(self):
        empresa = self.get_empresa()
        if not empresa:
            return PerfilAcesso.objects.none()
        return PerfilAcesso.objects.filter(empresa=empresa)


# ══════════════════════════════════════════════
# USUÁRIOS
# ══════════════════════════════════════════════

class UsuarioListView(EmpresaSessionMixin, ListView):
    model = Usuario
    template_name = "authentication/usuario_list.html"
    context_object_name = "objetos"
    paginate_by = 25

    def get_queryset(self):
        empresa = self.get_empresa()
        if not empresa:
            return Usuario.objects.none()
        qs = (
            Usuario.objects
            .filter(empresas_acesso__empresa=empresa, empresas_acesso__ativo=True)
            .select_related("perfil_acesso", "empresa_principal")
            .distinct()
            .order_by("nome")
        )
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(nome__icontains=q)
        ativo = self.request.GET.get("ativo")
        if ativo in ("true", "false"):
            qs = qs.filter(is_active=(ativo == "true"))
        return qs


class UsuarioCreateView(MensagemSucessoMixin, EmpresaSessionMixin, CreateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = "authentication/usuario_form.html"
    success_url = reverse_lazy("authentication:usuario_list")
    extra_context = {"titulo": "Novo Usuário"}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        empresa = self.get_empresa()
        if empresa:
            UsuarioEmpresa.objects.get_or_create(
                usuario=self.object,
                empresa=empresa,
                defaults={"perfil_acesso": self.object.perfil_acesso, "ativo": True},
            )
        return response


class UsuarioUpdateView(MensagemSucessoMixin, EmpresaSessionMixin, UpdateView):
    model = Usuario
    form_class = UsuarioEdicaoForm
    template_name = "authentication/usuario_form.html"
    success_url = reverse_lazy("authentication:usuario_list")
    extra_context = {"titulo": "Editar Usuário"}

    def get_queryset(self):
        empresa = self.get_empresa()
        if not empresa:
            return Usuario.objects.none()
        return Usuario.objects.filter(
            empresas_acesso__empresa=empresa,
            empresas_acesso__ativo=True,
        ).distinct()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs


class UsuarioDeleteView(MensagemSucessoMixin, EmpresaSessionMixin, DeleteView):
    """Soft delete — apenas desvincula o usuário da empresa ativa."""
    model = Usuario
    template_name = "authentication/confirmar_exclusao.html"
    success_url = reverse_lazy("authentication:usuario_list")

    def get_queryset(self):
        empresa = self.get_empresa()
        if not empresa:
            return Usuario.objects.none()
        return Usuario.objects.filter(
            empresas_acesso__empresa=empresa,
            empresas_acesso__ativo=True,
        ).distinct()

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        empresa = self.get_empresa()
        if empresa:
            UsuarioEmpresa.objects.filter(
                usuario=self.object, empresa=empresa
            ).update(ativo=False)
        messages.success(request, "Usuário removido da empresa com sucesso.")
        return redirect(self.success_url)


# ══════════════════════════════════════════════
# LOGS E NOTIFICAÇÕES
# ══════════════════════════════════════════════

class LogAuditoriaListView(EmpresaSessionMixin, ListView):
    model = LogAuditoria
    template_name = "authentication/log_list.html"
    context_object_name = "objetos"
    paginate_by = 50

    def get_queryset(self):
        empresa = self.get_empresa()
        if not empresa:
            return LogAuditoria.objects.none()
        qs = LogAuditoria.objects.filter(empresa=empresa).select_related("usuario").order_by("-criado_em")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(descricao__icontains=q)
        return qs


class NotificacaoListView(EmpresaSessionMixin, ListView):
    model = Notificacao
    template_name = "authentication/notificacao_list.html"
    context_object_name = "objetos"
    paginate_by = 30

    def get_queryset(self):
        return Notificacao.objects.filter(
            usuario=self.request.user
        ).order_by("-criado_em")


class NotificacaoMarcarLidaView(LoginRequiredMixin, View):
    def post(self, request, pk):
        Notificacao.objects.filter(pk=pk, usuario=request.user).update(lida=True)
        return redirect(request.POST.get("next", "authentication:dashboard"))


# ══════════════════════════════════════════════
# TABELAS DE DOMÍNIO — SUPERUSUÁRIO
# ══════════════════════════════════════════════

class SegmentoEmpresaListView(SuperuserRequiredMixin, ListView):
    model = SegmentoEmpresa
    template_name = "authentication/dominio_list.html"
    context_object_name = "objetos"
    extra_context = {
        "titulo": "Segmentos de Empresa",
        "create_url": "authentication:segmento_create",
        "update_url": "authentication:segmento_update",
        "delete_url": "authentication:segmento_delete",
    }

    def get_queryset(self):
        return SegmentoEmpresa.objects.all().order_by("nome")


class SegmentoEmpresaCreateView(MensagemSucessoMixin, SuperuserRequiredMixin, CreateView):
    model = SegmentoEmpresa
    form_class = SegmentoEmpresaForm
    template_name = "authentication/dominio_form.html"
    success_url = reverse_lazy("authentication:segmento_list")
    extra_context = {"titulo": "Novo Segmento", "list_url": "authentication:segmento_list"}


class SegmentoEmpresaUpdateView(MensagemSucessoMixin, SuperuserRequiredMixin, UpdateView):
    model = SegmentoEmpresa
    form_class = SegmentoEmpresaForm
    template_name = "authentication/dominio_form.html"
    success_url = reverse_lazy("authentication:segmento_list")
    extra_context = {"titulo": "Editar Segmento", "list_url": "authentication:segmento_list"}


class SegmentoEmpresaDeleteView(MensagemSucessoMixin, SuperuserRequiredMixin, DeleteView):
    model = SegmentoEmpresa
    template_name = "authentication/confirmar_exclusao.html"
    success_url = reverse_lazy("authentication:segmento_list")


class RegimeTributarioListView(SuperuserRequiredMixin, ListView):
    model = RegimeTributario
    template_name = "authentication/dominio_list.html"
    context_object_name = "objetos"
    extra_context = {
        "titulo": "Regimes Tributários",
        "create_url": "authentication:regime_create",
        "update_url": "authentication:regime_update",
        "delete_url": "authentication:regime_delete",
    }

    def get_queryset(self):
        return RegimeTributario.objects.all().order_by("nome")


class RegimeTributarioCreateView(MensagemSucessoMixin, SuperuserRequiredMixin, CreateView):
    model = RegimeTributario
    form_class = RegimeTributarioForm
    template_name = "authentication/dominio_form.html"
    success_url = reverse_lazy("authentication:regime_list")
    extra_context = {"titulo": "Novo Regime Tributário", "list_url": "authentication:regime_list"}


class RegimeTributarioUpdateView(MensagemSucessoMixin, SuperuserRequiredMixin, UpdateView):
    model = RegimeTributario
    form_class = RegimeTributarioForm
    template_name = "authentication/dominio_form.html"
    success_url = reverse_lazy("authentication:regime_list")
    extra_context = {"titulo": "Editar Regime Tributário", "list_url": "authentication:regime_list"}


class RegimeTributarioDeleteView(MensagemSucessoMixin, SuperuserRequiredMixin, DeleteView):
    model = RegimeTributario
    template_name = "authentication/confirmar_exclusao.html"
    success_url = reverse_lazy("authentication:regime_list")


# ══════════════════════════════════════════════
# TABELAS DE DOMÍNIO — POR EMPRESA
# ══════════════════════════════════════════════

class TipoDocumentoListView(EmpresaSessionMixin, ListView):
    model = TipoDocumento
    template_name = "authentication/dominio_list.html"
    context_object_name = "objetos"
    extra_context = {
        "titulo": "Tipos de Documento",
        "create_url": "authentication:tipo_documento_create",
        "update_url": "authentication:tipo_documento_update",
        "delete_url": "authentication:tipo_documento_delete",
    }

    def get_queryset(self):
        empresa = self.get_empresa()
        if not empresa:
            return TipoDocumento.objects.none()
        return TipoDocumento.objects.filter(empresa=empresa).order_by("nome")


class TipoDocumentoCreateView(MensagemSucessoMixin, EmpresaSessionMixin, CreateView):
    model = TipoDocumento
    form_class = TipoDocumentoForm
    template_name = "authentication/dominio_form.html"
    success_url = reverse_lazy("authentication:tipo_documento_list")
    extra_context = {"titulo": "Novo Tipo de Documento", "list_url": "authentication:tipo_documento_list"}

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        return super().form_valid(form)


class TipoDocumentoUpdateView(MensagemSucessoMixin, EmpresaSessionMixin, UpdateView):
    model = TipoDocumento
    form_class = TipoDocumentoForm
    template_name = "authentication/dominio_form.html"
    success_url = reverse_lazy("authentication:tipo_documento_list")
    extra_context = {"titulo": "Editar Tipo de Documento", "list_url": "authentication:tipo_documento_list"}

    def get_queryset(self):
        empresa = self.get_empresa()
        return TipoDocumento.objects.filter(empresa=empresa) if empresa else TipoDocumento.objects.none()


class TipoDocumentoDeleteView(MensagemSucessoMixin, EmpresaSessionMixin, DeleteView):
    model = TipoDocumento
    template_name = "authentication/confirmar_exclusao.html"
    success_url = reverse_lazy("authentication:tipo_documento_list")

    def get_queryset(self):
        empresa = self.get_empresa()
        return TipoDocumento.objects.filter(empresa=empresa) if empresa else TipoDocumento.objects.none()


class TipoContatoListView(EmpresaSessionMixin, ListView):
    model = TipoContato
    template_name = "authentication/dominio_list.html"
    context_object_name = "objetos"
    extra_context = {
        "titulo": "Tipos de Contato",
        "create_url": "authentication:tipo_contato_create",
        "update_url": "authentication:tipo_contato_update",
        "delete_url": "authentication:tipo_contato_delete",
    }

    def get_queryset(self):
        empresa = self.get_empresa()
        if not empresa:
            return TipoContato.objects.none()
        return TipoContato.objects.filter(empresa=empresa).order_by("nome")


class TipoContatoCreateView(MensagemSucessoMixin, EmpresaSessionMixin, CreateView):
    model = TipoContato
    form_class = TipoContatoForm
    template_name = "authentication/dominio_form.html"
    success_url = reverse_lazy("authentication:tipo_contato_list")
    extra_context = {"titulo": "Novo Tipo de Contato", "list_url": "authentication:tipo_contato_list"}

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        return super().form_valid(form)


class TipoContatoUpdateView(MensagemSucessoMixin, EmpresaSessionMixin, UpdateView):
    model = TipoContato
    form_class = TipoContatoForm
    template_name = "authentication/dominio_form.html"
    success_url = reverse_lazy("authentication:tipo_contato_list")
    extra_context = {"titulo": "Editar Tipo de Contato", "list_url": "authentication:tipo_contato_list"}

    def get_queryset(self):
        empresa = self.get_empresa()
        return TipoContato.objects.filter(empresa=empresa) if empresa else TipoContato.objects.none()


class TipoContatoDeleteView(MensagemSucessoMixin, EmpresaSessionMixin, DeleteView):
    model = TipoContato
    template_name = "authentication/confirmar_exclusao.html"
    success_url = reverse_lazy("authentication:tipo_contato_list")

    def get_queryset(self):
        empresa = self.get_empresa()
        return TipoContato.objects.filter(empresa=empresa) if empresa else TipoContato.objects.none()


class TipoNotificacaoListView(EmpresaSessionMixin, ListView):
    model = TipoNotificacao
    template_name = "authentication/dominio_list.html"
    context_object_name = "objetos"
    extra_context = {
        "titulo": "Tipos de Notificação",
        "create_url": "authentication:tipo_notificacao_create",
        "update_url": "authentication:tipo_notificacao_update",
        "delete_url": "authentication:tipo_notificacao_delete",
    }

    def get_queryset(self):
        empresa = self.get_empresa()
        if not empresa:
            return TipoNotificacao.objects.none()
        return TipoNotificacao.objects.filter(empresa=empresa).order_by("nome")


class TipoNotificacaoCreateView(MensagemSucessoMixin, EmpresaSessionMixin, CreateView):
    model = TipoNotificacao
    form_class = TipoNotificacaoForm
    template_name = "authentication/dominio_form.html"
    success_url = reverse_lazy("authentication:tipo_notificacao_list")
    extra_context = {"titulo": "Novo Tipo de Notificação", "list_url": "authentication:tipo_notificacao_list"}

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        return super().form_valid(form)


class TipoNotificacaoUpdateView(MensagemSucessoMixin, EmpresaSessionMixin, UpdateView):
    model = TipoNotificacao
    form_class = TipoNotificacaoForm
    template_name = "authentication/dominio_form.html"
    success_url = reverse_lazy("authentication:tipo_notificacao_list")
    extra_context = {"titulo": "Editar Tipo de Notificação", "list_url": "authentication:tipo_notificacao_list"}

    def get_queryset(self):
        empresa = self.get_empresa()
        return TipoNotificacao.objects.filter(empresa=empresa) if empresa else TipoNotificacao.objects.none()


class TipoNotificacaoDeleteView(MensagemSucessoMixin, EmpresaSessionMixin, DeleteView):
    model = TipoNotificacao
    template_name = "authentication/confirmar_exclusao.html"
    success_url = reverse_lazy("authentication:tipo_notificacao_list")

    def get_queryset(self):
        empresa = self.get_empresa()
        return TipoNotificacao.objects.filter(empresa=empresa) if empresa else TipoNotificacao.objects.none()


class TipoAcaoLogListView(SuperuserRequiredMixin, ListView):
    model = TipoAcaoLog
    template_name = "authentication/dominio_list.html"
    context_object_name = "objetos"
    extra_context = {
        "titulo": "Tipos de Ação de Log",
        "create_url": "authentication:tipo_acao_log_create",
        "update_url": "authentication:tipo_acao_log_update",
        "delete_url": "authentication:tipo_acao_log_delete",
    }

    def get_queryset(self):
        return TipoAcaoLog.objects.all().order_by("nome")


class TipoAcaoLogCreateView(MensagemSucessoMixin, SuperuserRequiredMixin, CreateView):
    model = TipoAcaoLog
    form_class = TipoAcaoLogForm
    template_name = "authentication/dominio_form.html"
    success_url = reverse_lazy("authentication:tipo_acao_log_list")
    extra_context = {"titulo": "Novo Tipo de Ação", "list_url": "authentication:tipo_acao_log_list"}


class TipoAcaoLogUpdateView(MensagemSucessoMixin, SuperuserRequiredMixin, UpdateView):
    model = TipoAcaoLog
    form_class = TipoAcaoLogForm
    template_name = "authentication/dominio_form.html"
    success_url = reverse_lazy("authentication:tipo_acao_log_list")
    extra_context = {"titulo": "Editar Tipo de Ação", "list_url": "authentication:tipo_acao_log_list"}


class TipoAcaoLogDeleteView(MensagemSucessoMixin, SuperuserRequiredMixin, DeleteView):
    model = TipoAcaoLog
    template_name = "authentication/confirmar_exclusao.html"
    success_url = reverse_lazy("authentication:tipo_acao_log_list")