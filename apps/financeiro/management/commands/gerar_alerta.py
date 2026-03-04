"""
manage.py gerar_alertas >> /var/log/alertas.log 2>&1
"""

from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q

from apps.authentication.models import (
    LogAuditoria, Notificacao, TipoNotificacao,
    TipoAcaoLog, UsuarioEmpresa,
)
from apps.financeiro.models import ContaPagar, ContaReceber
from apps.fiscal.models import ObrigacaoFiscal
from apps.sistema.models import Cliente


DIAS_ALERTA = [1, 3, 7]  # Dias antes do vencimento para alertar


class Command(BaseCommand):
    help = "Gera notificações automáticas de vencimento e inadimplência."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        hoje = date.today()

        self.stdout.write(
            self.style.NOTICE(
                f"[{timezone.now():%Y-%m-%d %H:%M}] Gerando alertas (dry_run={dry_run})"
            )
        )

        # Carrega tipos de notificação e ação de log (cria se não existir)
        tipo_vencimento = self._get_ou_criar_tipo_notif("Alerta de Vencimento", "bi-exclamation-triangle")
        tipo_inadimplencia = self._get_ou_criar_tipo_notif("Inadimplência", "bi-person-dash")
        tipo_fiscal = self._get_ou_criar_tipo_notif("Obrigação Fiscal", "bi-building-check")

        n_cp = self._alertas_contas_pagar(hoje, dry_run, tipo_vencimento, tipo_inadimplencia)
        n_cr = self._alertas_contas_receber(hoje, dry_run, tipo_vencimento, tipo_inadimplencia)
        n_fiscal = self._alertas_fiscal(hoje, dry_run, tipo_fiscal)
        n_cli = self._marcar_clientes_inadimplentes(hoje, dry_run)

        self.stdout.write(
            self.style.SUCCESS(
                f"Concluído: {n_cp} alertas CP | {n_cr} alertas CR | "
                f"{n_fiscal} alertas Fiscal | {n_cli} clientes marcados inadimplentes."
            )
        )

    # ──────────────────────────────────────────────
    # CONTAS A PAGAR
    # ──────────────────────────────────────────────

    def _alertas_contas_pagar(self, hoje, dry_run, tipo_venc, tipo_inad) -> int:
        total = 0

        # Próximas do vencimento
        for dias in DIAS_ALERTA:
            data_alvo = hoje + timedelta(days=dias)
            contas = ContaPagar.objects.filter(
                status__finalizado=False,
                data_vencimento=data_alvo,
            ).select_related("empresa", "fornecedor")

            for cp in contas:
                titulo = f"CP vence em {dias} dia(s): {cp.descricao[:50]}"
                msg = (
                    f"A conta a pagar '{cp.descricao}' "
                    f"{'do fornecedor ' + cp.fornecedor.razao_social if cp.fornecedor else ''} "
                    f"vence em {dias} dia(s) ({cp.data_vencimento:%d/%m/%Y}). "
                    f"Valor: R$ {cp.valor_original:,.2f}"
                )
                if not dry_run:
                    self._notificar_empresa(cp.empresa, tipo_venc, titulo, msg, "ContaPagar", cp.pk)
                self.stdout.write(f"  [CP-VENC] {titulo}")
                total += 1

        # Vencidas hoje ou antes
        vencidas = ContaPagar.objects.filter(
            status__finalizado=False,
            data_vencimento__lt=hoje,
        ).select_related("empresa", "fornecedor")

        for cp in vencidas:
            dias_atraso = (hoje - cp.data_vencimento).days
            if dias_atraso not in [1, 3, 7, 15, 30]:  # Alertas espaçados
                continue
            titulo = f"CP VENCIDA há {dias_atraso} dia(s): {cp.descricao[:40]}"
            msg = (
                f"ATENÇÃO: A conta a pagar '{cp.descricao}' está vencida há {dias_atraso} dia(s). "
                f"Vencimento: {cp.data_vencimento:%d/%m/%Y}. Valor: R$ {cp.valor_original:,.2f}"
            )
            if not dry_run:
                self._notificar_empresa(cp.empresa, tipo_inad, titulo, msg, "ContaPagar", cp.pk)
            self.stdout.write(f"  [CP-VENC-ATRASO] {titulo}")
            total += 1

        return total

    # ──────────────────────────────────────────────
    # CONTAS A RECEBER
    # ──────────────────────────────────────────────

    def _alertas_contas_receber(self, hoje, dry_run, tipo_venc, tipo_inad) -> int:
        total = 0

        # Próximas do vencimento
        for dias in DIAS_ALERTA:
            data_alvo = hoje + timedelta(days=dias)
            contas = ContaReceber.objects.filter(
                status__finalizado=False,
                data_vencimento=data_alvo,
            ).select_related("empresa", "cliente")

            for cr in contas:
                titulo = f"CR vence em {dias} dia(s): {cr.descricao[:50]}"
                msg = (
                    f"A conta a receber '{cr.descricao}' "
                    f"{'do cliente ' + cr.cliente.razao_social if cr.cliente else ''} "
                    f"vence em {dias} dia(s) ({cr.data_vencimento:%d/%m/%Y}). "
                    f"Valor: R$ {cr.valor_original:,.2f}"
                )
                if not dry_run:
                    self._notificar_empresa(cr.empresa, tipo_venc, titulo, msg, "ContaReceber", cr.pk)
                self.stdout.write(f"  [CR-VENC] {titulo}")
                total += 1

        # Vencidas (inadimplência)
        vencidas = ContaReceber.objects.filter(
            status__finalizado=False,
            data_vencimento__lt=hoje,
        ).select_related("empresa", "cliente")

        for cr in vencidas:
            dias_atraso = (hoje - cr.data_vencimento).days
            if dias_atraso not in [1, 3, 7, 15, 30]:
                continue
            titulo = f"CR INADIMPLENTE há {dias_atraso} dia(s): {cr.descricao[:40]}"
            msg = (
                f"INADIMPLÊNCIA: A conta a receber '{cr.descricao}' "
                f"{'do cliente ' + cr.cliente.razao_social if cr.cliente else ''} "
                f"está vencida há {dias_atraso} dia(s). "
                f"Vencimento: {cr.data_vencimento:%d/%m/%Y}. Valor: R$ {cr.valor_original:,.2f}"
            )
            if not dry_run:
                self._notificar_empresa(cr.empresa, tipo_inad, titulo, msg, "ContaReceber", cr.pk)
            self.stdout.write(f"  [CR-INADIMPL] {titulo}")
            total += 1

        return total

    # ──────────────────────────────────────────────
    # OBRIGAÇÕES FISCAIS
    # ──────────────────────────────────────────────

    def _alertas_fiscal(self, hoje, dry_run, tipo_fiscal) -> int:
        total = 0
        for dias in DIAS_ALERTA + [15]:
            data_alvo = hoje + timedelta(days=dias)
            obrigacoes = ObrigacaoFiscal.objects.filter(
                status__nome__icontains="Pendente",
                data_vencimento=data_alvo,
            ).select_related("empresa", "tipo", "status")

            for ob in obrigacoes:
                titulo = f"Obrigação fiscal vence em {dias} dia(s): {ob.tipo.sigla or ob.tipo.nome}"
                msg = (
                    f"A obrigação fiscal '{ob.tipo.nome}' vence em {dias} dia(s) "
                    f"({ob.data_vencimento:%d/%m/%Y}). Competência: {ob.competencia:%m/%Y}."
                )
                if not dry_run:
                    self._notificar_empresa(ob.empresa, tipo_fiscal, titulo, msg, "ObrigacaoFiscal", ob.pk)
                self.stdout.write(f"  [FISCAL] {titulo}")
                total += 1

        return total

    # ──────────────────────────────────────────────
    # MARCAR CLIENTES INADIMPLENTES
    # ──────────────────────────────────────────────

    def _marcar_clientes_inadimplentes(self, hoje, dry_run) -> int:
        """
        Marca clientes como inadimplentes se possuem CR vencida em aberto.
        Desmarca clientes sem CR vencida (adimplentes novamente).
        """
        total = 0

        # IDs de clientes com CR vencida em aberto
        clientes_com_atraso = set(
            ContaReceber.objects.filter(
                status__finalizado=False,
                data_vencimento__lt=hoje,
                cliente__isnull=False,
            ).values_list("cliente_id", flat=True)
        )

        # Marca inadimplentes
        if not dry_run:
            marcados = Cliente.objects.filter(
                pk__in=clientes_com_atraso,
                inadimplente=False,
            ).update(inadimplente=True)
            total += marcados

            # Desmarca adimplentes
            Cliente.objects.filter(
                inadimplente=True,
            ).exclude(
                pk__in=clientes_com_atraso,
            ).update(inadimplente=False)
        else:
            total = len(clientes_com_atraso)

        self.stdout.write(f"  [INADIMPLÊNCIA] {total} cliente(s) marcados/desmarcados.")
        return total

    # ──────────────────────────────────────────────
    # Utilitários
    # ──────────────────────────────────────────────

    @staticmethod
    def _get_ou_criar_tipo_notif(nome: str, icone: str) -> "TipoNotificacao":
        obj, _ = TipoNotificacao.objects.get_or_create(
            nome=nome,
            defaults={"icone": icone},
        )
        return obj

    @staticmethod
    def _notificar_empresa(empresa, tipo, titulo, mensagem, objeto_tipo="", objeto_id=None):
        """Cria notificação para todos os usuários ativos da empresa."""
        usuarios_ativos = UsuarioEmpresa.objects.filter(
            empresa=empresa, ativo=True
        ).select_related("usuario")

        notificacoes = [
            Notificacao(
                empresa=empresa,
                usuario=ue.usuario,
                tipo=tipo,
                titulo=titulo,
                mensagem=mensagem,
                objeto_tipo=objeto_tipo,
                objeto_id=objeto_id,
            )
            for ue in usuarios_ativos
        ]
        if notificacoes:
            Notificacao.objects.bulk_create(notificacoes, ignore_conflicts=True)