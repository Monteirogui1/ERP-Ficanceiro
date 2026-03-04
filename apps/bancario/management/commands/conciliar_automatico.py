from django.core.management.base import BaseCommand, CommandError
from apps.bancario.models import ImportacaoExtrato
from apps.bancario.services.conciliacao_automatica import ConciliacaoAutomaticaService

class Command(BaseCommand):
    help = "Executa conciliação automática em uma importação de extrato."

    def add_arguments(self, parser):
        parser.add_argument("--importacao-id", type=int, required=True)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        try:
            importacao = ImportacaoExtrato.objects.get(pk=options["importacao_id"])
        except ImportacaoExtrato.DoesNotExist:
            raise CommandError(f"Importação #{options['importacao_id']} não encontrada.")

        svc = ConciliacaoAutomaticaService(importacao, dry_run=options["dry_run"])
        resultado = svc.executar()
        self.stdout.write(self.style.SUCCESS(str(resultado)))

