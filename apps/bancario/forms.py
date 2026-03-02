from django import forms
from .models import (
    TipoArquivoBancario, StatusConciliacao, TipoMovimentoBancario,
    ImportacaoExtrato, ConciliacaoBancaria,
    ArquivoRemessa, ArquivoRetorno,
)
from apps.sistema.models import ContaBancaria
from apps.financeiro.models import LancamentoFinanceiro


# ══════════════════════════════════════════════
# TABELAS DE DOMÍNIO
# ══════════════════════════════════════════════

class TipoArquivoBancarioForm(forms.ModelForm):
    class Meta:
        model = TipoArquivoBancario
        fields = ["nome", "extensao", "ativo"]

    def clean_nome(self):
        nome = self.cleaned_data["nome"]
        qs = TipoArquivoBancario.objects.filter(nome__iexact=nome)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe um tipo de arquivo com este nome.")
        return nome


class StatusConciliacaoForm(forms.ModelForm):
    class Meta:
        model = StatusConciliacao
        fields = ["nome", "ativo"]

    def clean_nome(self):
        nome = self.cleaned_data["nome"]
        qs = StatusConciliacao.objects.filter(nome__iexact=nome)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe um status de conciliação com este nome.")
        return nome


class TipoMovimentoBancarioForm(forms.ModelForm):
    class Meta:
        model = TipoMovimentoBancario
        fields = ["nome", "natureza", "ativo"]

    def clean_nome(self):
        nome = self.cleaned_data["nome"]
        qs = TipoMovimentoBancario.objects.filter(nome__iexact=nome)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe um tipo de movimento com este nome.")
        return nome


# ══════════════════════════════════════════════
# IMPORTAÇÃO DE EXTRATOS
# ══════════════════════════════════════════════

EXTENSOES_PERMITIDAS = [".ofx", ".cnab", ".ret", ".csv", ".txt"]


class ImportacaoExtratoForm(forms.ModelForm):
    class Meta:
        model = ImportacaoExtrato
        fields = ["conta_bancaria", "tipo_arquivo", "arquivo", "nome_arquivo",
                  "data_inicio_extrato", "data_fim_extrato"]
        widgets = {
            "data_inicio_extrato": forms.DateInput(attrs={"type": "date"}),
            "data_fim_extrato": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields["conta_bancaria"].queryset = ContaBancaria.objects.filter(
                empresa=empresa, ativo=True
            )
        for f in ["data_inicio_extrato", "data_fim_extrato", "nome_arquivo"]:
            self.fields[f].required = False

    def clean_arquivo(self):
        arquivo = self.cleaned_data.get("arquivo")
        if arquivo:
            import os
            ext = os.path.splitext(arquivo.name)[1].lower()
            if ext not in EXTENSOES_PERMITIDAS:
                raise forms.ValidationError(
                    f"Extensão não permitida. Use: {', '.join(EXTENSOES_PERMITIDAS)}"
                )
            if arquivo.size > 50 * 1024 * 1024:
                raise forms.ValidationError("O arquivo não pode ter mais de 50MB.")
        return arquivo

    def clean(self):
        cleaned = super().clean()
        inicio = cleaned.get("data_inicio_extrato")
        fim = cleaned.get("data_fim_extrato")
        if inicio and fim and fim < inicio:
            self.add_error("data_fim_extrato", "A data fim não pode ser anterior à data início.")
        return cleaned


# ══════════════════════════════════════════════
# CONCILIAÇÃO BANCÁRIA
# ══════════════════════════════════════════════

class ConciliacaoBancariaForm(forms.ModelForm):
    class Meta:
        model = ConciliacaoBancaria
        fields = [
            "movimento_bancario", "lancamento",
            "status", "automatica", "diferenca", "observacao",
        ]
        widgets = {
            "observacao": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            from .models import MovimentoBancario, StatusConciliacao
            self.fields["movimento_bancario"].queryset = MovimentoBancario.objects.filter(
                conta_bancaria__empresa=empresa
            ).select_related("conta_bancaria")
            self.fields["lancamento"].queryset = LancamentoFinanceiro.objects.filter(
                empresa=empresa, conciliado=False
            ).order_by("-data_lancamento")
            self.fields["status"].queryset = StatusConciliacao.objects.filter(ativo=True)
        self.fields["diferenca"].required = False
        self.fields["observacao"].required = False


# ══════════════════════════════════════════════
# REMESSA E RETORNO
# ══════════════════════════════════════════════

class ArquivoRemessaForm(forms.ModelForm):
    class Meta:
        model = ArquivoRemessa
        fields = [
            "conta_bancaria", "tipo", "nome_arquivo",
            "numero_sequencial", "valor_total",
        ]

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields["conta_bancaria"].queryset = ContaBancaria.objects.filter(
                empresa=empresa, ativo=True
            )

    def clean_valor_total(self):
        valor = self.cleaned_data["valor_total"]
        if valor < 0:
            raise forms.ValidationError("O valor total não pode ser negativo.")
        return valor


class ArquivoRetornoForm(forms.ModelForm):
    class Meta:
        model = ArquivoRetorno
        fields = [
            "conta_bancaria", "arquivo_remessa",
            "nome_arquivo", "arquivo",
        ]

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields["conta_bancaria"].queryset = ContaBancaria.objects.filter(
                empresa=empresa, ativo=True
            )
            self.fields["arquivo_remessa"].queryset = ArquivoRemessa.objects.filter(
                empresa=empresa
            ).order_by("-criado_em")
        self.fields["arquivo_remessa"].required = False

    def clean_arquivo(self):
        arquivo = self.cleaned_data.get("arquivo")
        if arquivo:
            import os
            ext = os.path.splitext(arquivo.name)[1].lower()
            if ext not in EXTENSOES_PERMITIDAS:
                raise forms.ValidationError(
                    f"Extensão não permitida. Use: {', '.join(EXTENSOES_PERMITIDAS)}"
                )
        return arquivo