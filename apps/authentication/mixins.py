from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy


class EmpresaMixin(LoginRequiredMixin):
    """
    Garante que o usuário está autenticado e filtra todos os
    querysets pela empresa ativa na sessão.
    """

    def get_empresa(self):
        empresa_id = self.request.session.get("empresa_ativa_id")
        if not empresa_id:
            raise PermissionDenied("Nenhuma empresa ativa na sessão.")
        return self.request.user.empresas_acesso.get(empresa_id=empresa_id).empresa

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(empresa=self.get_empresa())

    def form_valid(self, form):
        if hasattr(form.instance, "empresa"):
            form.instance.empresa = self.get_empresa()
        if hasattr(form.instance, "criado_por"):
            form.instance.criado_por = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["empresa"] = self.get_empresa()
        return ctx


class PermissaoModuloMixin(EmpresaMixin):
    """
    Verifica se o perfil do usuário tem permissão para o módulo.
    Defina `modulo` e `acao` nas subclasses.
    Ex: modulo = "contas_pagar" | acao = "ver"
    """
    modulo = None
    acao = "ver"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and self.modulo:
            perfil = request.user.perfil_acesso
            if perfil:
                perms = perfil.permissoes.get(self.modulo, {})
                if not perms.get(self.acao, False):
                    raise PermissionDenied(
                        f"Sem permissão de '{self.acao}' no módulo '{self.modulo}'."
                    )
        return super().dispatch(request, *args, **kwargs)