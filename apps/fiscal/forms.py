from django import forms
from .models import (
    TipoImposto, TipoObrigacaoFiscal, StatusObrigacaoFiscal,
    ConfiguracaoImpostoEmpresa, LancamentoImposto, ObrigacaoFiscal,
)
from apps.sistema.models import PlanoContas
from apps.authentication.models import Usuario


# ══════════════════════════════════════════════
# TABELAS DE DOMÍNIO
# ══════════════════════════════════════════════

class TipoImpostoForm(forms.ModelForm):
    class Meta:
        model = TipoImposto
        fields = ["nome", "sigla", "esfera", "base_calculo_padrao", "ativo"]
        widgets = {
            "base_calculo_padrao": forms.TextInput(
                attrs={"placeholder": "Ex: Receita Bruta, Folha de Pagamento"}
            ),
        }

    def clean_sigla(self):
        sigla = self.cleaned_data["sigla"].upper()
        qs = TipoImposto.objects.filter(sigla__iexact=sigla)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe um imposto com esta sigla.")
        return sigla

    def clean_nome(self):
        nome = self.cleaned_data["nome"]
        qs = TipoImposto.objects.filter(nome__iexact=nome)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe um imposto com este nome.")
        return nome


class TipoObrigacaoFiscalForm(forms.ModelForm):
    class Meta:
        model = TipoObrigacaoFiscal
        fields = ["nome", "sigla", "periodicidade", "ativo"]

    def clean_nome(self):
        nome = self.cleaned_data["nome"]
        qs = TipoObrigacaoFiscal.objects.filter(nome__iexact=nome)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe uma obrigação fiscal com este nome.")
        return nome


class StatusObrigacaoFiscalForm(forms.ModelForm):
    class Meta:
        model = StatusObrigacaoFiscal
        fields = ["nome", "ativo"]

    def clean_nome(self):
        nome = self.cleaned_data["nome"]
        qs = StatusObrigacaoFiscal.objects.filter(nome__iexact=nome)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe um status com este nome.")
        return nome


# ══════════════════════════════════════════════
# CONFIGURAÇÃO DE IMPOSTOS
# ══════════════════════════════════════════════

class ConfiguracaoImpostoEmpresaForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoImpostoEmpresa
        fields = [
            "tipo_imposto", "aliquota",
            "plano_contas_debito", "plano_contas_credito",
            "vigencia_inicio", "vigencia_fim", "ativo",
        ]
        widgets = {
            "vigencia_inicio": forms.DateInput(attrs={"type": "date"}),
            "vigencia_fim": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa
        if empresa:
            contas = PlanoContas.objects.filter(
                empresa=empresa, analitica=True, ativo=True
            ).order_by("codigo")
            self.fields["plano_contas_debito"].queryset = contas
            self.fields["plano_contas_credito"].queryset = contas
        for f in ["plano_contas_debito", "plano_contas_credito", "vigencia_fim"]:
            self.fields[f].required = False

    def clean_aliquota(self):
        aliquota = self.cleaned_data["aliquota"]
        if aliquota < 0 or aliquota > 100:
            raise forms.ValidationError("A alíquota deve estar entre 0 e 100%.")
        return aliquota

    def clean(self):
        cleaned = super().clean()
        inicio = cleaned.get("vigencia_inicio")
        fim = cleaned.get("vigencia_fim")
        if inicio and fim and fim <= inicio:
            self.add_error("vigencia_fim", "A data fim deve ser posterior à data de início.")

        tipo = cleaned.get("tipo_imposto")
        if tipo and inicio and self.empresa:
            qs = ConfiguracaoImpostoEmpresa.objects.filter(
                empresa=self.empresa,
                tipo_imposto=tipo,
                vigencia_inicio=inicio,
            )
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(
                    "Já existe uma configuração para este imposto nesta data de vigência."
                )
        return cleaned


# ══════════════════════════════════════════════
# LANÇAMENTOS DE IMPOSTOS
# ══════════════════════════════════════════════

class LancamentoImpostoForm(forms.ModelForm):
    class Meta:
        model = LancamentoImposto
        fields = [
            "tipo_imposto", "configuracao", "competencia", "data_vencimento",
            "base_calculo", "aliquota_aplicada", "valor_calculado",
            "valor_pago", "data_pagamento", "numero_guia", "observacoes",
        ]
        widgets = {
            "competencia": forms.DateInput(attrs={"type": "date"}),
            "data_vencimento": forms.DateInput(attrs={"type": "date"}),
            "data_pagamento": forms.DateInput(attrs={"type": "date"}),
            "observacoes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa
        if empresa:
            self.fields["configuracao"].queryset = ConfiguracaoImpostoEmpresa.objects.filter(
                empresa=empresa, ativo=True
            ).select_related("tipo_imposto").order_by("tipo_imposto__sigla")
        for f in ["configuracao", "valor_pago", "data_pagamento", "numero_guia", "observacoes"]:
            self.fields[f].required = False

    def clean(self):
        cleaned = super().clean()
        base = cleaned.get("base_calculo")
        aliquota = cleaned.get("aliquota_aplicada")
        valor = cleaned.get("valor_calculado")
        if base and aliquota and valor:
            esperado = round(base * aliquota / 100, 2)
            if abs(float(valor) - float(esperado)) > 0.05:
                self.add_error(
                    "valor_calculado",
                    f"O valor calculado ({valor}) difere do esperado ({esperado}) "
                    f"com base no percentual informado."
                )
        valor_pago = cleaned.get("valor_pago")
        data_pagamento = cleaned.get("data_pagamento")
        if valor_pago and valor_pago > 0 and not data_pagamento:
            self.add_error("data_pagamento", "Informe a data de pagamento.")
        return cleaned


# ══════════════════════════════════════════════
# OBRIGAÇÕES FISCAIS
# ══════════════════════════════════════════════

class ObrigacaoFiscalForm(forms.ModelForm):
    class Meta:
        model = ObrigacaoFiscal
        fields = [
            "tipo", "status", "competencia", "data_vencimento",
            "data_entrega", "numero_protocolo",
            "arquivo", "responsavel", "observacoes",
        ]
        widgets = {
            "competencia": forms.DateInput(attrs={"type": "date"}),
            "data_vencimento": forms.DateInput(attrs={"type": "date"}),
            "data_entrega": forms.DateInput(attrs={"type": "date"}),
            "observacoes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa
        self.fields["status"].queryset = StatusObrigacaoFiscal.objects.filter(ativo=True)
        if empresa:
            self.fields["responsavel"].queryset = Usuario.objects.filter(
                empresas_acesso__empresa=empresa,
                empresas_acesso__ativo=True,
                is_active=True,
            ).distinct().order_by("nome")
        for f in ["data_entrega", "numero_protocolo", "arquivo", "responsavel", "observacoes"]:
            self.fields[f].required = False

    def clean(self):
        cleaned = super().clean()
        competencia = cleaned.get("competencia")
        vencimento = cleaned.get("data_vencimento")
        if competencia and vencimento and vencimento < competencia:
            self.add_error(
                "data_vencimento",
                "A data de vencimento não pode ser anterior à competência."
            )
        entrega = cleaned.get("data_entrega")
        if entrega and vencimento and entrega > vencimento:
            self.add_error(
                "data_entrega",
                "A entrega após o vencimento indica atraso — confirme se está correto."
            )
        return cleaned