from django.core.management import call_command
from apps.bancario.models import ArquivoRetorno
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender="bancario.ArquivoRetorno")
def auto_processar_retorno(sender, instance, created, **kwargs):
    if created:
        from django.core.management import call_command
        import threading
        # Executa em thread separada para não bloquear o request
        t = threading.Thread(
            target=call_command,
            args=("processar_retorno",),
            kwargs={"importacao_id": instance.pk},
        )
        t.daemon = True
        t.start()
