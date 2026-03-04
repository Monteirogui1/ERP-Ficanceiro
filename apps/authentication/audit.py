import json
from django.forms import model_to_dict
from django.utils import timezone

from apps.authentication.models import LogAuditoria, TipoAcaoLog


# ──────────────────────────────────────────────
# Função utilitária central
# ──────────────────────────────────────────────

def registrar_log(
    request,
    modulo: str,
    acao: str,
    descricao: str,
    objeto=None,
    dados_anteriores: dict = None,
    dados_novos: dict = None,
):
    """
    Registra um LogAuditoria.

    Args:
        request:          HttpRequest Django
        modulo:           Nome do módulo (ex: "contas_pagar")
        acao:             Nome da ação (ex: "CRIAÇÃO", "EDIÇÃO", "EXCLUSÃO")
        descricao:        Descrição legível do evento
        objeto:           Instância do model relacionado (opcional)
        dados_anteriores: Dict com estado anterior do objeto (opcional)
        dados_novos:      Dict com estado novo do objeto (opcional)
    """
    empresa = None
    usuario = None

    if request and hasattr(request, "user") and request.user.is_authenticated:
        usuario = request.user
        empresa_id = request.session.get("empresa_ativa_id")
        if empresa_id:
            from apps.authentication.models import UsuarioEmpresa
            try:
                ue = request.user.empresas_acesso.get(empresa_id=empresa_id, ativo=True)
                empresa = ue.empresa
            except Exception:
                pass

    if not empresa:
        return  # Não registra sem empresa ativa

    tipo_acao, _ = TipoAcaoLog.objects.get_or_create(
        nome=acao.upper(),
        defaults={"descricao": f"Ação automática: {acao}"},
    )

    objeto_tipo = ""
    objeto_id = None
    if objeto is not None:
        objeto_tipo = objeto.__class__.__name__
        objeto_id = getattr(objeto, "pk", None)

    # Captura IP
    ip = None
    if request:
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        ip = x_forwarded.split(",")[0] if x_forwarded else request.META.get("REMOTE_ADDR")

    LogAuditoria.objects.create(
        empresa=empresa,
        usuario=usuario,
        tipo_acao=tipo_acao,
        modulo=modulo,
        objeto_tipo=objeto_tipo,
        objeto_id=objeto_id,
        descricao=descricao,
        dados_anteriores=dados_anteriores,
        dados_novos=dados_novos,
        ip_address=ip,
        user_agent=request.META.get("HTTP_USER_AGENT", "") if request else "",
    )


def _serializar_objeto(obj) -> dict:
    """Converte um model instance em dict JSON-safe para auditoria."""
    try:
        data = model_to_dict(obj)
        # Converte tipos não-serializáveis
        result = {}
        for k, v in data.items():
            if hasattr(v, "pk"):
                result[k] = v.pk
            elif hasattr(v, "isoformat"):
                result[k] = v.isoformat()
            elif hasattr(v, "__iter__") and not isinstance(v, str):
                result[k] = list(v)
            else:
                try:
                    json.dumps(v)
                    result[k] = v
                except (TypeError, ValueError):
                    result[k] = str(v)
        return result
    except Exception:
        return {}


# ──────────────────────────────────────────────
# Mixin para Class-Based Views
# ──────────────────────────────────────────────

class AuditMixin:
    """
    Mixin para CBVs Django que registra automaticamente logs de auditoria
    em criação, edição e exclusão.

    Atributos configuráveis:
        modulo (str): nome do módulo financeiro (ex: "contas_pagar")
        audit_descricao_criar (str): template de mensagem para criação
        audit_descricao_editar (str): template de mensagem para edição
        audit_descricao_excluir (str): template de mensagem para exclusão
    """
    modulo: str = "sistema"
    audit_descricao_criar: str = "Registro criado."
    audit_descricao_editar: str = "Registro atualizado."
    audit_descricao_excluir: str = "Registro excluído."

    # ── Criação e Edição ──────────────────────

    def form_valid(self, form):
        is_new = not form.instance.pk

        # Captura estado anterior (para edição)
        dados_anteriores = None
        if not is_new:
            try:
                anterior = form.instance.__class__.objects.get(pk=form.instance.pk)
                dados_anteriores = _serializar_objeto(anterior)
            except Exception:
                pass

        response = super().form_valid(form)

        # Captura estado novo após salvar
        dados_novos = _serializar_objeto(form.instance)

        acao = "CRIAÇÃO" if is_new else "EDIÇÃO"
        descricao = (
            self._audit_descricao(form.instance, is_new)
        )

        registrar_log(
            request=self.request,
            modulo=self.modulo,
            acao=acao,
            descricao=descricao,
            objeto=form.instance,
            dados_anteriores=dados_anteriores,
            dados_novos=dados_novos,
        )

        return response

    def _audit_descricao(self, obj, is_new: bool) -> str:
        template = self.audit_descricao_criar if is_new else self.audit_descricao_editar
        try:
            return template.format(obj=obj)
        except Exception:
            return template

    # ── Exclusão ─────────────────────────────

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        dados_anteriores = _serializar_objeto(obj)

        response = super().delete(request, *args, **kwargs)

        registrar_log(
            request=request,
            modulo=self.modulo,
            acao="EXCLUSÃO",
            descricao=self._audit_descricao_excluir(obj),
            objeto=obj,
            dados_anteriores=dados_anteriores,
        )

        return response

    def _audit_descricao_excluir(self, obj) -> str:
        try:
            return self.audit_descricao_excluir.format(obj=obj)
        except Exception:
            return self.audit_descricao_excluir


# ──────────────────────────────────────────────
# Decorator para funções/views simples
# ──────────────────────────────────────────────

def audit_action(modulo: str, acao: str, descricao_fn=None):
    """
    Decorator para views baseadas em função.

    Uso:
        @audit_action("bancario", "IMPORTAÇÃO", lambda req, *a, **kw: "Extrato importado")
        def minha_view(request): ...
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            desc = descricao_fn(request, *args, **kwargs) if descricao_fn else f"{acao} em {modulo}"
            registrar_log(request, modulo, acao, desc)
            return response
        wrapper.__name__ = view_func.__name__
        return wrapper
    return decorator