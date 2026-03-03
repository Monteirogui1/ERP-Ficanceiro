from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, Q, F, DecimalField, Value
from django.db.models.functions import Coalesce, TruncMonth
from django.utils import timezone
from django.http import JsonResponse
from datetime import date, timedelta
from decimal import Decimal
import json

from apps.authentication.mixins import EmpresaMixin
from apps.financeiro.models import (
    ContaPagar, ContaReceber, LancamentoFinanceiro,
    StatusContaPagar, StatusContaReceber, TipoLancamento
)
from apps.sistema.models import ContaBancaria, CentroCusto, PlanoContas
from apps.orcamento.models import ItemOrcamento, Orcamento
from apps.fiscal.models import LancamentoImposto


# ══════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════

def _empresa(request):
    empresa_id = request.session.get("empresa_ativa_id")
    if not empresa_id:
        return None
    try:
        return request.user.empresas_acesso.get(empresa_id=empresa_id).empresa
    except Exception:
        return None


def _fmt(valor):
    """Converte Decimal/None para float seguro para JSON."""
    if valor is None:
        return 0.0
    return float(valor)


# ══════════════════════════════════════════════
# DASHBOARD PRINCIPAL
# ══════════════════════════════════════════════

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "home/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empresa = _empresa(self.request)
        if not empresa:
            return ctx

        hoje = date.today()
        inicio_mes = hoje.replace(day=1)
        proximo_mes = (inicio_mes + timedelta(days=32)).replace(day=1)
        sete_dias = hoje + timedelta(days=7)

        # ── KPIs principais ──────────────────────────────
        # Contas a Pagar
        cp_vencer = ContaPagar.objects.filter(
            empresa=empresa,
            status__finalizado=False,
            data_vencimento__gte=hoje,
            data_vencimento__lte=sete_dias,
        ).aggregate(total=Coalesce(Sum('valor_original'), Decimal('0')))['total']

        cp_vencidas = ContaPagar.objects.filter(
            empresa=empresa,
            status__finalizado=False,
            data_vencimento__lt=hoje,
        ).aggregate(total=Coalesce(Sum('valor_original'), Decimal('0')))['total']

        # Contas a Receber
        cr_vencer = ContaReceber.objects.filter(
            empresa=empresa,
            status__finalizado=False,
            data_vencimento__gte=hoje,
            data_vencimento__lte=sete_dias,
        ).aggregate(total=Coalesce(Sum('valor_original'), Decimal('0')))['total']

        cr_vencidas = ContaReceber.objects.filter(
            empresa=empresa,
            status__finalizado=False,
            data_vencimento__lt=hoje,
        ).aggregate(total=Coalesce(Sum('valor_original'), Decimal('0')))['total']

        # Saldo total em contas bancárias
        saldo_total = ContaBancaria.objects.filter(
            empresa=empresa, ativo=True
        ).aggregate(total=Coalesce(Sum('saldo_atual'), Decimal('0')))['total']

        # ── Fluxo do mês atual ───────────────────────────
        lancamentos_mes = LancamentoFinanceiro.objects.filter(
            empresa=empresa,
            data_lancamento__gte=inicio_mes,
            data_lancamento__lt=proximo_mes,
        ).select_related('tipo_lancamento')

        entradas_mes = lancamentos_mes.filter(
            tipo_lancamento__natureza='C'
        ).aggregate(total=Coalesce(Sum('valor'), Decimal('0')))['total']

        saidas_mes = lancamentos_mes.filter(
            tipo_lancamento__natureza='D'
        ).aggregate(total=Coalesce(Sum('valor'), Decimal('0')))['total']

        # ── Gráfico: Fluxo de Caixa últimos 6 meses ─────
        seis_meses_atras = hoje - timedelta(days=180)
        fluxo_mensal = (
            LancamentoFinanceiro.objects
            .filter(empresa=empresa, data_lancamento__gte=seis_meses_atras)
            .annotate(mes=TruncMonth('data_lancamento'))
            .values('mes', 'tipo_lancamento__natureza')
            .annotate(total=Sum('valor'))
            .order_by('mes')
        )

        meses_label = []
        entradas_chart = []
        saidas_chart = []
        meses_data = {}
        for item in fluxo_mensal:
            mes_key = item['mes'].strftime('%m/%Y')
            if mes_key not in meses_data:
                meses_data[mes_key] = {'C': 0, 'D': 0}
            nat = item['tipo_lancamento__natureza'] or 'D'
            meses_data[mes_key][nat] += _fmt(item['total'])

        for mes_key, vals in sorted(meses_data.items()):
            meses_label.append(mes_key)
            entradas_chart.append(vals['C'])
            saidas_chart.append(vals['D'])

        # ── Gráfico: CP por status (pizza) ───────────────
        cp_status = (
            ContaPagar.objects.filter(empresa=empresa)
            .values('status__nome')
            .annotate(total=Sum('valor_original'))
            .order_by('-total')[:6]
        )
        cp_status_labels = [x['status__nome'] or 'Sem status' for x in cp_status]
        cp_status_values = [_fmt(x['total']) for x in cp_status]

        # ── Próximos vencimentos CP ──────────────────────
        prox_cp = ContaPagar.objects.filter(
            empresa=empresa,
            status__finalizado=False,
            data_vencimento__gte=hoje,
        ).select_related('fornecedor', 'status').order_by('data_vencimento')[:8]

        # ── Próximos vencimentos CR ──────────────────────
        prox_cr = ContaReceber.objects.filter(
            empresa=empresa,
            status__finalizado=False,
            data_vencimento__gte=hoje,
        ).select_related('cliente', 'status').order_by('data_vencimento')[:8]

        # ── Contas bancárias ─────────────────────────────
        contas = ContaBancaria.objects.filter(empresa=empresa, ativo=True).select_related('banco', 'tipo_conta')

        ctx.update({
            # KPIs
            'cp_vencer': cp_vencer,
            'cp_vencidas': cp_vencidas,
            'cr_vencer': cr_vencer,
            'cr_vencidas': cr_vencidas,
            'saldo_total': saldo_total,
            'entradas_mes': entradas_mes,
            'saidas_mes': saidas_mes,
            'resultado_mes': entradas_mes - saidas_mes,
            # Gráficos (JSON para Chart.js)
            'fluxo_labels': json.dumps(meses_label),
            'fluxo_entradas': json.dumps(entradas_chart),
            'fluxo_saidas': json.dumps(saidas_chart),
            'cp_status_labels': json.dumps(cp_status_labels),
            'cp_status_values': json.dumps(cp_status_values),
            # Listas
            'prox_cp': prox_cp,
            'prox_cr': prox_cr,
            'contas': contas,
            'hoje': hoje,
        })
        return ctx


# ══════════════════════════════════════════════
# RELATÓRIO: DRE
# ══════════════════════════════════════════════

class RelatorioDREView(LoginRequiredMixin, TemplateView):
    template_name = "home/relatorios/dre.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empresa = _empresa(self.request)
        if not empresa:
            return ctx

        hoje = date.today()
        ano = int(self.request.GET.get('ano', hoje.year))
        mes_ini = int(self.request.GET.get('mes_ini', 1))
        mes_fim = int(self.request.GET.get('mes_fim', hoje.month))

        data_ini = date(ano, mes_ini, 1)
        # último dia do mês final
        if mes_fim == 12:
            data_fim = date(ano + 1, 1, 1) - timedelta(days=1)
        else:
            data_fim = date(ano, mes_fim + 1, 1) - timedelta(days=1)

        lancamentos = LancamentoFinanceiro.objects.filter(
            empresa=empresa,
            data_competencia__gte=data_ini,
            data_competencia__lte=data_fim,
        ).select_related('plano_contas__tipo', 'tipo_lancamento')

        # Agrupa por plano de contas
        por_plano = (
            lancamentos
            .values(
                'plano_contas__codigo',
                'plano_contas__nome',
                'plano_contas__tipo__nome',
                'plano_contas__tipo__natureza',
                'tipo_lancamento__natureza',
            )
            .annotate(total=Sum('valor'))
            .order_by('plano_contas__codigo')
        )

        receitas = []
        despesas = []
        total_receitas = Decimal('0')
        total_despesas = Decimal('0')

        for item in por_plano:
            nome_tipo = item['plano_contas__tipo__nome'] or ''
            natureza_tipo = item['plano_contas__tipo__natureza'] or 'D'
            total = item['total'] or Decimal('0')

            linha = {
                'codigo': item['plano_contas__codigo'] or '-',
                'nome': item['plano_contas__nome'] or 'Sem plano',
                'total': total,
            }

            # Natureza C = credora = receita
            if natureza_tipo == 'C':
                receitas.append(linha)
                total_receitas += total
            else:
                despesas.append(linha)
                total_despesas += total

        resultado = total_receitas - total_despesas

        # Gráfico mensal de resultado
        resultado_mensal = (
            LancamentoFinanceiro.objects
            .filter(empresa=empresa, data_competencia__year=ano)
            .annotate(mes=TruncMonth('data_competencia'))
            .values('mes', 'tipo_lancamento__natureza')
            .annotate(total=Sum('valor'))
            .order_by('mes')
        )
        meses_dre = {}
        for item in resultado_mensal:
            if not item['mes']:
                continue
            mk = item['mes'].strftime('%m/%Y')
            if mk not in meses_dre:
                meses_dre[mk] = {'C': 0, 'D': 0}
            nat = item['tipo_lancamento__natureza'] or 'D'
            meses_dre[mk][nat] += _fmt(item['total'])

        dre_labels = []
        dre_resultado = []
        for mk, v in sorted(meses_dre.items()):
            dre_labels.append(mk)
            dre_resultado.append(round(v['C'] - v['D'], 2))

        ctx.update({
            'receitas': receitas,
            'despesas': despesas,
            'total_receitas': total_receitas,
            'total_despesas': total_despesas,
            'resultado': resultado,
            'ano': ano,
            'mes_ini': mes_ini,
            'mes_fim': mes_fim,
            'anos': range(hoje.year - 4, hoje.year + 2),
            'meses': range(1, 13),
            'dre_labels': json.dumps(dre_labels),
            'dre_resultado': json.dumps(dre_resultado),
        })
        return ctx


# ══════════════════════════════════════════════
# RELATÓRIO: FLUXO DE CAIXA
# ══════════════════════════════════════════════

class RelatorioFluxoCaixaView(LoginRequiredMixin, TemplateView):
    template_name = "home/relatorios/fluxo_caixa.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empresa = _empresa(self.request)
        if not empresa:
            return ctx

        hoje = date.today()
        periodo = self.request.GET.get('periodo', '30')
        try:
            dias = int(periodo)
        except ValueError:
            dias = 30

        data_ini = hoje - timedelta(days=dias)
        data_fim = hoje + timedelta(days=dias)

        # Realizados
        lancamentos = (
            LancamentoFinanceiro.objects
            .filter(empresa=empresa, data_lancamento__gte=data_ini, data_lancamento__lte=hoje)
            .select_related('tipo_lancamento', 'conta_bancaria', 'plano_contas')
            .order_by('data_lancamento')
        )

        # Previsto (contas a pagar e receber em aberto)
        cp_previstas = ContaPagar.objects.filter(
            empresa=empresa,
            status__finalizado=False,
            data_vencimento__gte=hoje,
            data_vencimento__lte=data_fim,
        ).select_related('fornecedor').order_by('data_vencimento')

        cr_previstas = ContaReceber.objects.filter(
            empresa=empresa,
            status__finalizado=False,
            data_vencimento__gte=hoje,
            data_vencimento__lte=data_fim,
        ).select_related('cliente').order_by('data_vencimento')

        # Saldo por conta bancária
        contas = ContaBancaria.objects.filter(empresa=empresa, ativo=True).select_related('banco')

        # Gráfico acumulado diário
        diario = {}
        for lanc in lancamentos:
            dk = lanc.data_lancamento.strftime('%d/%m')
            if dk not in diario:
                diario[dk] = {'entrada': 0, 'saida': 0}
            nat = lanc.tipo_lancamento.natureza if lanc.tipo_lancamento else 'D'
            if nat == 'C':
                diario[dk]['entrada'] += _fmt(lanc.valor)
            else:
                diario[dk]['saida'] += _fmt(lanc.valor)

        dias_labels = list(diario.keys())
        entradas_dia = [diario[d]['entrada'] for d in dias_labels]
        saidas_dia = [diario[d]['saida'] for d in dias_labels]

        # Totais
        total_entradas = sum(entradas_dia)
        total_saidas = sum(saidas_dia)
        saldo_periodo = total_entradas - total_saidas

        ctx.update({
            'lancamentos': lancamentos,
            'cp_previstas': cp_previstas,
            'cr_previstas': cr_previstas,
            'contas': contas,
            'total_entradas': total_entradas,
            'total_saidas': total_saidas,
            'saldo_periodo': saldo_periodo,
            'periodo': periodo,
            'hoje': hoje,
            'data_fim': data_fim,
            'dias_labels': json.dumps(dias_labels),
            'entradas_dia': json.dumps(entradas_dia),
            'saidas_dia': json.dumps(saidas_dia),
        })
        return ctx


# ══════════════════════════════════════════════
# RELATÓRIO: INADIMPLÊNCIA
# ══════════════════════════════════════════════

class RelatorioInadimplenciaView(LoginRequiredMixin, TemplateView):
    template_name = "home/relatorios/inadimplencia.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empresa = _empresa(self.request)
        if not empresa:
            return ctx

        hoje = date.today()

        inadimplentes = (
            ContaReceber.objects.filter(
                empresa=empresa,
                status__finalizado=False,
                data_vencimento__lt=hoje,
            )
            .select_related('cliente', 'status')
            .order_by('data_vencimento')
        )

        # Faixas de atraso
        faixa_1_30 = []
        faixa_31_60 = []
        faixa_61_90 = []
        faixa_90_mais = []

        for cr in inadimplentes:
            dias_atraso = (hoje - cr.data_vencimento).days
            cr.dias_atraso = dias_atraso
            if dias_atraso <= 30:
                faixa_1_30.append(cr)
            elif dias_atraso <= 60:
                faixa_31_60.append(cr)
            elif dias_atraso <= 90:
                faixa_61_90.append(cr)
            else:
                faixa_90_mais.append(cr)

        total_inadimplente = sum(cr.valor_original for cr in inadimplentes)

        # Top 10 clientes inadimplentes
        top_clientes = (
            ContaReceber.objects.filter(
                empresa=empresa,
                status__finalizado=False,
                data_vencimento__lt=hoje,
            )
            .values('cliente__razao_social')
            .annotate(total=Sum('valor_original'), qtd=Count('id'))
            .order_by('-total')[:10]
        )

        # Gráfico de faixas
        faixas_labels = ['1-30 dias', '31-60 dias', '61-90 dias', '90+ dias']
        faixas_values = [
            _fmt(sum(cr.valor_original for cr in faixa_1_30)),
            _fmt(sum(cr.valor_original for cr in faixa_31_60)),
            _fmt(sum(cr.valor_original for cr in faixa_61_90)),
            _fmt(sum(cr.valor_original for cr in faixa_90_mais)),
        ]

        ctx.update({
            'inadimplentes': inadimplentes,
            'faixa_1_30': faixa_1_30,
            'faixa_31_60': faixa_31_60,
            'faixa_61_90': faixa_61_90,
            'faixa_90_mais': faixa_90_mais,
            'total_inadimplente': total_inadimplente,
            'top_clientes': top_clientes,
            'faixas_labels': json.dumps(faixas_labels),
            'faixas_values': json.dumps(faixas_values),
            'hoje': hoje,
        })
        return ctx


# ══════════════════════════════════════════════
# RELATÓRIO: CENTRO DE CUSTO
# ══════════════════════════════════════════════

class RelatorioCentroCustoView(LoginRequiredMixin, TemplateView):
    template_name = "home/relatorios/centro_custo.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empresa = _empresa(self.request)
        if not empresa:
            return ctx

        hoje = date.today()
        ano = int(self.request.GET.get('ano', hoje.year))

        # Orçamento x realizado por centro de custo
        orcamento_atual = Orcamento.objects.filter(empresa=empresa, ano=ano).first()

        centros = CentroCusto.objects.filter(empresa=empresa, ativo=True)

        dados_centros = []
        for cc in centros:
            previsto = Decimal('0')
            realizado_orc = Decimal('0')

            if orcamento_atual:
                itens = ItemOrcamento.objects.filter(
                    orcamento=orcamento_atual, centro_custo=cc
                ).aggregate(
                    prev=Coalesce(Sum('valor_previsto'), Decimal('0')),
                    real=Coalesce(Sum('valor_realizado'), Decimal('0')),
                )
                previsto = itens['prev']
                realizado_orc = itens['real']

            # Lançamentos reais do ano
            realizado_lancamentos = LancamentoFinanceiro.objects.filter(
                empresa=empresa,
                centro_custo=cc,
                data_lancamento__year=ano,
                tipo_lancamento__natureza='D',
            ).aggregate(total=Coalesce(Sum('valor'), Decimal('0')))['total']

            dados_centros.append({
                'centro': cc,
                'previsto': previsto,
                'realizado': realizado_lancamentos,
                'variacao': realizado_lancamentos - previsto,
                'perc': round((realizado_lancamentos / previsto * 100), 1) if previsto > 0 else 0,
            })

        # Gráfico
        cc_labels = [d['centro'].nome for d in dados_centros]
        cc_previsto = [_fmt(d['previsto']) for d in dados_centros]
        cc_realizado = [_fmt(d['realizado']) for d in dados_centros]

        ctx.update({
            'dados_centros': dados_centros,
            'ano': ano,
            'anos': range(hoje.year - 4, hoje.year + 2),
            'orcamento': orcamento_atual,
            'cc_labels': json.dumps(cc_labels),
            'cc_previsto': json.dumps(cc_previsto),
            'cc_realizado': json.dumps(cc_realizado),
        })
        return ctx


# ══════════════════════════════════════════════
# RELATÓRIO: CONTAS A PAGAR
# ══════════════════════════════════════════════

class RelatorioContasPagarView(LoginRequiredMixin, TemplateView):
    template_name = "home/relatorios/contas_pagar.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empresa = _empresa(self.request)
        if not empresa:
            return ctx

        hoje = date.today()
        status_id = self.request.GET.get('status')
        data_ini = self.request.GET.get('data_ini', (hoje.replace(day=1)).strftime('%Y-%m-%d'))
        data_fim = self.request.GET.get('data_fim', hoje.strftime('%Y-%m-%d'))

        qs = ContaPagar.objects.filter(
            empresa=empresa,
            data_vencimento__gte=data_ini,
            data_vencimento__lte=data_fim,
        ).select_related('fornecedor', 'status', 'plano_contas', 'centro_custo')

        if status_id:
            qs = qs.filter(status_id=status_id)

        totais = qs.aggregate(
            total_original=Coalesce(Sum('valor_original'), Decimal('0')),
            total_pago=Coalesce(Sum('valor_pago'), Decimal('0')),
        )
        total_pendente = totais['total_original'] - totais['total_pago']

        # Por fornecedor (top 10)
        por_fornecedor = (
            qs.values('fornecedor__razao_social')
            .annotate(total=Sum('valor_original'), qtd=Count('id'))
            .order_by('-total')[:10]
        )

        # Por status
        por_status = (
            qs.values('status__nome')
            .annotate(total=Sum('valor_original'), qtd=Count('id'))
            .order_by('-total')
        )

        status_labels = [x['status__nome'] or 'Sem status' for x in por_status]
        status_values = [_fmt(x['total']) for x in por_status]

        ctx.update({
            'contas': qs.order_by('data_vencimento'),
            'total_original': totais['total_original'],
            'total_pago': totais['total_pago'],
            'total_pendente': total_pendente,
            'por_fornecedor': por_fornecedor,
            'status_list': StatusContaPagar.objects.filter(ativo=True),
            'status_id': status_id,
            'data_ini': data_ini,
            'data_fim': data_fim,
            'status_labels': json.dumps(status_labels),
            'status_values': json.dumps(status_values),
            'hoje': hoje,
        })
        return ctx


# ══════════════════════════════════════════════
# RELATÓRIO: CONTAS A RECEBER
# ══════════════════════════════════════════════

class RelatorioContasReceberView(LoginRequiredMixin, TemplateView):
    template_name = "home/relatorios/contas_receber.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empresa = _empresa(self.request)
        if not empresa:
            return ctx

        hoje = date.today()
        status_id = self.request.GET.get('status')
        data_ini = self.request.GET.get('data_ini', (hoje.replace(day=1)).strftime('%Y-%m-%d'))
        data_fim = self.request.GET.get('data_fim', hoje.strftime('%Y-%m-%d'))

        qs = ContaReceber.objects.filter(
            empresa=empresa,
            data_vencimento__gte=data_ini,
            data_vencimento__lte=data_fim,
        ).select_related('cliente', 'status', 'plano_contas', 'centro_custo')

        if status_id:
            qs = qs.filter(status_id=status_id)

        totais = qs.aggregate(
            total_original=Coalesce(Sum('valor_original'), Decimal('0')),
            total_recebido=Coalesce(Sum('valor_recebido'), Decimal('0')),
        )
        total_pendente = totais['total_original'] - totais['total_recebido']

        por_cliente = (
            qs.values('cliente__razao_social')
            .annotate(total=Sum('valor_original'), qtd=Count('id'))
            .order_by('-total')[:10]
        )

        por_status = (
            qs.values('status__nome')
            .annotate(total=Sum('valor_original'), qtd=Count('id'))
            .order_by('-total')
        )

        status_labels = [x['status__nome'] or 'Sem status' for x in por_status]
        status_values = [_fmt(x['total']) for x in por_status]

        ctx.update({
            'contas': qs.order_by('data_vencimento'),
            'total_original': totais['total_original'],
            'total_recebido': totais['total_recebido'],
            'total_pendente': total_pendente,
            'por_cliente': por_cliente,
            'status_list': StatusContaReceber.objects.filter(ativo=True),
            'status_id': status_id,
            'data_ini': data_ini,
            'data_fim': data_fim,
            'status_labels': json.dumps(status_labels),
            'status_values': json.dumps(status_values),
            'hoje': hoje,
        })
        return ctx


# ══════════════════════════════════════════════
# RELATÓRIO: IMPOSTOS
# ══════════════════════════════════════════════

class RelatorioImpostosView(LoginRequiredMixin, TemplateView):
    template_name = "home/relatorios/impostos.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empresa = _empresa(self.request)
        if not empresa:
            return ctx

        hoje = date.today()
        ano = int(self.request.GET.get('ano', hoje.year))

        lancamentos = LancamentoImposto.objects.filter(
            empresa=empresa,
            competencia__year=ano,
        ).select_related('tipo_imposto').order_by('competencia')

        por_tipo = (
            lancamentos
            .values('tipo_imposto__nome', 'tipo_imposto__sigla')
            .annotate(
                total_calculado=Coalesce(Sum('valor_calculado'), Decimal('0')),
                total_pago=Coalesce(Sum('valor_pago'), Decimal('0')),
            )
            .order_by('-total_calculado')
        )

        total_calculado = sum(x['total_calculado'] for x in por_tipo)
        total_pago = sum(x['total_pago'] for x in por_tipo)
        total_pendente = total_calculado - total_pago

        # Próximos vencimentos de impostos
        proximos = LancamentoImposto.objects.filter(
            empresa=empresa,
            data_vencimento__gte=hoje,
            valor_pago=0,
        ).select_related('tipo_imposto').order_by('data_vencimento')[:10]

        imp_labels = [x['tipo_imposto__sigla'] or x['tipo_imposto__nome'] for x in por_tipo]
        imp_values = [_fmt(x['total_calculado']) for x in por_tipo]

        ctx.update({
            'lancamentos': lancamentos,
            'por_tipo': por_tipo,
            'total_calculado': total_calculado,
            'total_pago': total_pago,
            'total_pendente': total_pendente,
            'proximos': proximos,
            'ano': ano,
            'anos': range(hoje.year - 4, hoje.year + 2),
            'imp_labels': json.dumps(imp_labels),
            'imp_values': json.dumps(imp_values),
        })
        return ctx