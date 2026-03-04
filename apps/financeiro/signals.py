from django.db import transaction
from django.db.models import Sum, Q
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from decimal import Decimal

from apps.sistema.models import ContaBancaria
from .models import LancamentoFinanceiro


# ──────────────────────────────────────────────
# Utilitário central: recalcula o saldo de uma conta
# ──────────────────────────────────────────────

def _recalcular_saldo(conta_bancaria_id: int) -> None:
    """
    Recalcula saldo_atual de uma ContaBancaria com base em:
      saldo_inicial + soma(créditos) - soma(débitos)
    Executa em transação atômica para evitar race conditions.
    """
    with transaction.atomic():
        try:
            conta = ContaBancaria.objects.select_for_update().get(pk=conta_bancaria_id)
        except ContaBancaria.DoesNotExist:
            return

        lancamentos = LancamentoFinanceiro.objects.filter(
            conta_bancaria_id=conta_bancaria_id
        ).select_related("tipo_lancamento")

        creditos = lancamentos.filter(
            tipo_lancamento__natureza="C"
        ).aggregate(total=Sum("valor"))["total"] or Decimal("0")

        debitos = lancamentos.filter(
            tipo_lancamento__natureza="D"
        ).aggregate(total=Sum("valor"))["total"] or Decimal("0")

        conta.saldo_atual = conta.saldo_inicial + creditos - debitos
        conta.save(update_fields=["saldo_atual"])


# ──────────────────────────────────────────────
# Guarda conta anterior antes de salvar (update)
# ──────────────────────────────────────────────

@receiver(pre_save, sender=LancamentoFinanceiro)
def _lanc_pre_save(sender, instance, **kwargs):
    """Salva id da conta anterior para atualizar saldo da conta antiga em caso de troca."""
    instance._conta_anterior_id = None
    if instance.pk:
        try:
            anterior = LancamentoFinanceiro.objects.get(pk=instance.pk)
            instance._conta_anterior_id = anterior.conta_bancaria_id
        except LancamentoFinanceiro.DoesNotExist:
            pass


# ──────────────────────────────────────────────
# Após criar ou atualizar
# ──────────────────────────────────────────────

@receiver(post_save, sender=LancamentoFinanceiro)
def _lanc_post_save(sender, instance, created, **kwargs):
    contas_afetadas = {instance.conta_bancaria_id}

    # Se a conta foi trocada, recalcula a conta antiga também
    if not created and instance._conta_anterior_id:
        contas_afetadas.add(instance._conta_anterior_id)

    for conta_id in contas_afetadas:
        if conta_id:
            _recalcular_saldo(conta_id)


# ──────────────────────────────────────────────
# Após excluir
# ──────────────────────────────────────────────

@receiver(post_delete, sender=LancamentoFinanceiro)
def _lanc_post_delete(sender, instance, **kwargs):
    if instance.conta_bancaria_id:
        _recalcular_saldo(instance.conta_bancaria_id)