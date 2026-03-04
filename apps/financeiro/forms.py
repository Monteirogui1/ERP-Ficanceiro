from django import forms
from .models import (
    TipoDocumentoFinanceiro, TipoLancamento, FormaPagamento,
    StatusContaPagar, StatusContaReceber,
    PeriodicidadeRecorrencia, TipoEncargo, TipoCenarioFluxo,
    ContaPagar, EncargoContaPagar, DocumentoContaPagar,
    ContaReceber, EncargoContaReceber, DocumentoContaReceber,
    LancamentoFinanceiro, TransferenciaBancaria, ProjecaoFluxoCaixa,
)
from apps.sistema.models import (
    Fornecedor, Cliente, ContaBancaria, PlanoContas, CentroCusto
)

FC = "form-control"
FS = "form-select"


# ══════════════════════════════════════════════
# TABELAS DE DOMÍNIO
# ══════════════════════════════════════════════

class TipoDocumentoFinanceiroForm(forms.ModelForm):
    class Meta:
        model = TipoDocumentoFinanceiro
        fields = ["nome", "requer_numero_documento", "ativo"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": FC, "placeholder": "Ex: Boleto, Nota Fiscal, Contrato"}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa

    def clean_nome(self):
        nome = self.cleaned_data["nome"]
        qs = TipoDocumentoFinanceiro.objects.filter(empresa=self.empresa, nome__iexact=nome)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe um tipo de documento com este nome.")
        return nome


class FormaPagamentoForm(forms.ModelForm):
    class Meta:
        model = FormaPagamento
        fields = ["nome", "gera_arquivo_remessa", "ativo"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": FC, "placeholder": "Ex: Boleto, PIX, TED, Cartão"}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa

    def clean_nome(self):
        nome = self.cleaned_data["nome"]
        qs = FormaPagamento.objects.filter(empresa=self.empresa, nome__iexact=nome)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe uma forma de pagamento com este nome.")
        return nome


class StatusContaPagarForm(forms.ModelForm):
    class Meta:
        model = StatusContaPagar
        fields = ["nome", "finalizado", "ativo"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": FC, "placeholder": "Ex: Pendente, Pago, Cancelado"}),
        }

    def clean_nome(self):
        nome = self.cleaned_data["nome"]
        qs = StatusContaPagar.objects.filter(nome__iexact=nome)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe um status com este nome.")
        return nome


class StatusContaReceberForm(forms.ModelForm):
    class Meta:
        model = StatusContaReceber
        fields = ["nome", "finalizado", "ativo"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": FC, "placeholder": "Ex: Aberto, Recebido, Inadimplente"}),
        }

    def clean_nome(self):
        nome = self.cleaned_data["nome"]
        qs = StatusContaReceber.objects.filter(nome__iexact=nome)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe um status com este nome.")
        return nome


class PeriodicidadeRecorrenciaForm(forms.ModelForm):
    class Meta:
        model = PeriodicidadeRecorrencia
        fields = ["nome", "dias_intervalo", "ativo"]
        widgets = {
            "nome":           forms.TextInput(attrs={"class": FC, "placeholder": "Ex: Mensal, Quinzenal, Semanal"}),
            "dias_intervalo": forms.NumberInput(attrs={"class": FC, "placeholder": "Ex: 30", "min": "1"}),
        }

    def clean_nome(self):
        nome = self.cleaned_data["nome"]
        qs = PeriodicidadeRecorrencia.objects.filter(nome__iexact=nome)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe uma periodicidade com este nome.")
        return nome


class TipoEncargoForm(forms.ModelForm):
    class Meta:
        model = TipoEncargo
        fields = ["nome", "natureza", "ativo"]
        widgets = {
            "nome":     forms.TextInput(attrs={"class": FC, "placeholder": "Ex: Juros, Multa, Desconto"}),
            "natureza": forms.Select(attrs={"class": FS}),
        }

    def clean_nome(self):
        nome = self.cleaned_data["nome"]
        qs = TipoEncargo.objects.filter(nome__iexact=nome)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe um tipo de encargo com este nome.")
        return nome


class TipoCenarioFluxoForm(forms.ModelForm):
    class Meta:
        model = TipoCenarioFluxo
        fields = ["nome", "percentual_ajuste", "ativo"]
        widgets = {
            "nome":               forms.TextInput(attrs={"class": FC, "placeholder": "Ex: Otimista, Realista, Pessimista"}),
            "percentual_ajuste":  forms.NumberInput(attrs={"class": FC, "placeholder": "Ex: 10.00", "step": "0.01"}),
        }

    def clean_nome(self):
        nome = self.cleaned_data["nome"]
        qs = TipoCenarioFluxo.objects.filter(nome__iexact=nome)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe um cenário com este nome.")
        return nome


# ══════════════════════════════════════════════
# CONTAS A PAGAR
# ══════════════════════════════════════════════

class ContaPagarForm(forms.ModelForm):
    class Meta:
        model = ContaPagar
        fields = [
            "fornecedor", "tipo_documento", "numero_documento", "descricao",
            "plano_contas", "centro_custo", "conta_bancaria", "forma_pagamento", "status",
            "valor_original", "data_emissao", "data_vencimento", "data_competencia",
            "numero_parcelas", "numero_parcela_atual",
            "recorrente", "periodicidade", "data_fim_recorrencia",
            "requer_aprovacao", "observacoes",
        ]
        widgets = {
            "fornecedor":           forms.Select(attrs={"class": FS}),
            "tipo_documento":       forms.Select(attrs={"class": FS}),
            "numero_documento":     forms.TextInput(attrs={"class": FC, "placeholder": "Nº do documento"}),
            "descricao":            forms.TextInput(attrs={"class": FC, "placeholder": "Descrição da conta a pagar"}),
            "plano_contas":         forms.Select(attrs={"class": FS}),
            "centro_custo":         forms.Select(attrs={"class": FS}),
            "conta_bancaria":       forms.Select(attrs={"class": FS}),
            "forma_pagamento":      forms.Select(attrs={"class": FS}),
            "status":               forms.Select(attrs={"class": FS}),
            "valor_original":       forms.NumberInput(attrs={"class": FC, "placeholder": "0,00", "step": "0.01"}),
            "data_emissao":         forms.DateInput(attrs={"class": FC, "type": "date"}),
            "data_vencimento":      forms.DateInput(attrs={"class": FC, "type": "date"}),
            "data_competencia":     forms.DateInput(attrs={"class": FC, "type": "date"}),
            "data_fim_recorrencia": forms.DateInput(attrs={"class": FC, "type": "date"}),
            "numero_parcelas":      forms.NumberInput(attrs={"class": FC, "placeholder": "Ex: 12", "min": "1"}),
            "numero_parcela_atual": forms.NumberInput(attrs={"class": FC, "placeholder": "Ex: 1", "min": "1"}),
            "periodicidade":        forms.Select(attrs={"class": FS}),
            "observacoes":          forms.Textarea(attrs={"class": FC, "rows": 3, "placeholder": "Observações adicionais"}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields["fornecedor"].queryset = Fornecedor.objects.filter(
                empresa=empresa, ativo=True
            ).order_by("razao_social")
            self.fields["plano_contas"].queryset = PlanoContas.objects.filter(
                empresa=empresa, analitica=True, aceita_lancamentos=True, ativo=True
            ).order_by("codigo")
            self.fields["centro_custo"].queryset = CentroCusto.objects.filter(
                empresa=empresa, ativo=True
            ).order_by("codigo")
            self.fields["conta_bancaria"].queryset = ContaBancaria.objects.filter(
                empresa=empresa, ativo=True
            )
            self.fields["forma_pagamento"].queryset = FormaPagamento.objects.filter(
                empresa=empresa, ativo=True
            )
            self.fields["tipo_documento"].queryset = TipoDocumentoFinanceiro.objects.filter(
                empresa=empresa, ativo=True
            )
        for f in ["fornecedor", "tipo_documento", "numero_documento", "plano_contas",
                  "centro_custo", "conta_bancaria", "forma_pagamento",
                  "data_competencia", "periodicidade", "data_fim_recorrencia"]:
            self.fields[f].required = False

    def clean(self):
        cleaned = super().clean()
        recorrente = cleaned.get("recorrente")
        periodicidade = cleaned.get("periodicidade")
        if recorrente and not periodicidade:
            self.add_error("periodicidade", "Informe a periodicidade para lançamentos recorrentes.")
        return cleaned


class EncargoContaPagarForm(forms.ModelForm):
    class Meta:
        model = EncargoContaPagar
        fields = ["tipo_encargo", "percentual", "valor", "data_aplicacao", "observacao"]
        widgets = {
            "tipo_encargo":   forms.Select(attrs={"class": FS}),
            "percentual":     forms.NumberInput(attrs={"class": FC, "placeholder": "Ex: 2.00", "step": "0.01"}),
            "valor":          forms.NumberInput(attrs={"class": FC, "placeholder": "0,00", "step": "0.01"}),
            "data_aplicacao": forms.DateInput(attrs={"class": FC, "type": "date"}),
            "observacao":     forms.Textarea(attrs={"class": FC, "rows": 2, "placeholder": "Observações sobre o encargo"}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["percentual"].required = False

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("percentual") and not cleaned.get("valor"):
            raise forms.ValidationError("Informe o percentual ou o valor do encargo.")
        return cleaned


class DocumentoContaPagarForm(forms.ModelForm):
    class Meta:
        model = DocumentoContaPagar
        fields = ["nome", "arquivo"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": FC, "placeholder": "Nome ou descrição do documento"}),
        }

    def clean_arquivo(self):
        arquivo = self.cleaned_data.get("arquivo")
        if arquivo:
            max_mb = 10
            if arquivo.size > max_mb * 1024 * 1024:
                raise forms.ValidationError(f"O arquivo não pode ter mais de {max_mb}MB.")
        return arquivo


# ══════════════════════════════════════════════
# CONTAS A RECEBER
# ══════════════════════════════════════════════

class ContaReceberForm(forms.ModelForm):
    class Meta:
        model = ContaReceber
        fields = [
            "cliente", "tipo_documento", "numero_documento", "descricao",
            "plano_contas", "centro_custo", "conta_bancaria", "forma_pagamento", "status",
            "valor_original", "data_emissao", "data_vencimento", "data_competencia",
            "numero_parcelas", "numero_parcela_atual",
            "recorrente", "periodicidade", "data_fim_recorrencia",
            "nosso_numero", "em_cobranca", "observacoes",
        ]
        widgets = {
            "cliente":              forms.Select(attrs={"class": FS}),
            "tipo_documento":       forms.Select(attrs={"class": FS}),
            "numero_documento":     forms.TextInput(attrs={"class": FC, "placeholder": "Nº do documento"}),
            "descricao":            forms.TextInput(attrs={"class": FC, "placeholder": "Descrição da conta a receber"}),
            "plano_contas":         forms.Select(attrs={"class": FS}),
            "centro_custo":         forms.Select(attrs={"class": FS}),
            "conta_bancaria":       forms.Select(attrs={"class": FS}),
            "forma_pagamento":      forms.Select(attrs={"class": FS}),
            "status":               forms.Select(attrs={"class": FS}),
            "valor_original":       forms.NumberInput(attrs={"class": FC, "placeholder": "0,00", "step": "0.01"}),
            "data_emissao":         forms.DateInput(attrs={"class": FC, "type": "date"}),
            "data_vencimento":      forms.DateInput(attrs={"class": FC, "type": "date"}),
            "data_competencia":     forms.DateInput(attrs={"class": FC, "type": "date"}),
            "data_fim_recorrencia": forms.DateInput(attrs={"class": FC, "type": "date"}),
            "numero_parcelas":      forms.NumberInput(attrs={"class": FC, "placeholder": "Ex: 12", "min": "1"}),
            "numero_parcela_atual": forms.NumberInput(attrs={"class": FC, "placeholder": "Ex: 1", "min": "1"}),
            "periodicidade":        forms.Select(attrs={"class": FS}),
            "nosso_numero":         forms.TextInput(attrs={"class": FC, "placeholder": "Nosso número (cobrança bancária)"}),
            "observacoes":          forms.Textarea(attrs={"class": FC, "rows": 3, "placeholder": "Observações adicionais"}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields["cliente"].queryset = Cliente.objects.filter(
                empresa=empresa, ativo=True
            ).order_by("razao_social")
            self.fields["plano_contas"].queryset = PlanoContas.objects.filter(
                empresa=empresa, analitica=True, aceita_lancamentos=True, ativo=True
            ).order_by("codigo")
            self.fields["centro_custo"].queryset = CentroCusto.objects.filter(
                empresa=empresa, ativo=True
            ).order_by("codigo")
            self.fields["conta_bancaria"].queryset = ContaBancaria.objects.filter(
                empresa=empresa, ativo=True
            )
            self.fields["forma_pagamento"].queryset = FormaPagamento.objects.filter(
                empresa=empresa, ativo=True
            )
            self.fields["tipo_documento"].queryset = TipoDocumentoFinanceiro.objects.filter(
                empresa=empresa, ativo=True
            )
        for f in ["cliente", "tipo_documento", "numero_documento", "plano_contas",
                  "centro_custo", "conta_bancaria", "forma_pagamento",
                  "data_competencia", "periodicidade", "data_fim_recorrencia", "nosso_numero"]:
            self.fields[f].required = False

    def clean(self):
        cleaned = super().clean()
        recorrente = cleaned.get("recorrente")
        periodicidade = cleaned.get("periodicidade")
        if recorrente and not periodicidade:
            self.add_error("periodicidade", "Informe a periodicidade para lançamentos recorrentes.")
        return cleaned


class EncargoContaReceberForm(forms.ModelForm):
    class Meta:
        model = EncargoContaReceber
        fields = ["tipo_encargo", "percentual", "valor", "data_aplicacao", "observacao"]
        widgets = {
            "tipo_encargo":   forms.Select(attrs={"class": FS}),
            "percentual":     forms.NumberInput(attrs={"class": FC, "placeholder": "Ex: 2.00", "step": "0.01"}),
            "valor":          forms.NumberInput(attrs={"class": FC, "placeholder": "0,00", "step": "0.01"}),
            "data_aplicacao": forms.DateInput(attrs={"class": FC, "type": "date"}),
            "observacao":     forms.Textarea(attrs={"class": FC, "rows": 2, "placeholder": "Observações sobre o encargo"}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["percentual"].required = False

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("percentual") and not cleaned.get("valor"):
            raise forms.ValidationError("Informe o percentual ou o valor do encargo.")
        return cleaned


class DocumentoContaReceberForm(forms.ModelForm):
    class Meta:
        model = DocumentoContaReceber
        fields = ["nome", "arquivo"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": FC, "placeholder": "Nome ou descrição do documento"}),
        }

    def clean_arquivo(self):
        arquivo = self.cleaned_data.get("arquivo")
        if arquivo:
            if arquivo.size > 10 * 1024 * 1024:
                raise forms.ValidationError("O arquivo não pode ter mais de 10MB.")
        return arquivo


# ══════════════════════════════════════════════
# LANÇAMENTOS FINANCEIROS
# ══════════════════════════════════════════════

class LancamentoFinanceiroForm(forms.ModelForm):
    class Meta:
        model = LancamentoFinanceiro
        fields = [
            "conta_bancaria", "tipo_lancamento", "plano_contas", "centro_custo",
            "descricao", "valor", "data_lancamento", "data_competencia",
            "numero_documento", "observacoes",
        ]
        widgets = {
            "conta_bancaria":   forms.Select(attrs={"class": FS}),
            "tipo_lancamento":  forms.Select(attrs={"class": FS}),
            "plano_contas":     forms.Select(attrs={"class": FS}),
            "centro_custo":     forms.Select(attrs={"class": FS}),
            "descricao":        forms.TextInput(attrs={"class": FC, "placeholder": "Descrição do lançamento"}),
            "valor":            forms.NumberInput(attrs={"class": FC, "placeholder": "0,00", "step": "0.01"}),
            "data_lancamento":  forms.DateInput(attrs={"class": FC, "type": "date"}),
            "data_competencia": forms.DateInput(attrs={"class": FC, "type": "date"}),
            "numero_documento": forms.TextInput(attrs={"class": FC, "placeholder": "Nº do documento (opcional)"}),
            "observacoes":      forms.Textarea(attrs={"class": FC, "rows": 3, "placeholder": "Observações adicionais"}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields["conta_bancaria"].queryset = ContaBancaria.objects.filter(
                empresa=empresa, ativo=True
            )
            self.fields["plano_contas"].queryset = PlanoContas.objects.filter(
                empresa=empresa, analitica=True, aceita_lancamentos=True, ativo=True
            ).order_by("codigo")
            self.fields["centro_custo"].queryset = CentroCusto.objects.filter(
                empresa=empresa, ativo=True
            ).order_by("codigo")
        for f in ["plano_contas", "centro_custo", "data_competencia", "numero_documento"]:
            self.fields[f].required = False

    def clean_valor(self):
        valor = self.cleaned_data["valor"]
        if valor == 0:
            raise forms.ValidationError("O valor do lançamento não pode ser zero.")
        return valor


# ══════════════════════════════════════════════
# TRANSFERÊNCIAS BANCÁRIAS
# ══════════════════════════════════════════════

class TransferenciaBancariaForm(forms.ModelForm):
    class Meta:
        model = TransferenciaBancaria
        fields = [
            "conta_origem", "conta_destino",
            "valor", "data_transferencia", "descricao",
        ]
        widgets = {
            "conta_origem":       forms.Select(attrs={"class": FS}),
            "conta_destino":      forms.Select(attrs={"class": FS}),
            "valor":              forms.NumberInput(attrs={"class": FC, "placeholder": "0,00", "step": "0.01"}),
            "data_transferencia": forms.DateInput(attrs={"class": FC, "type": "date"}),
            "descricao":          forms.TextInput(attrs={"class": FC, "placeholder": "Descrição da transferência (opcional)"}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            qs = ContaBancaria.objects.filter(empresa=empresa, ativo=True)
            self.fields["conta_origem"].queryset = qs
            self.fields["conta_destino"].queryset = qs
        self.fields["descricao"].required = False

    def clean(self):
        cleaned = super().clean()
        origem  = cleaned.get("conta_origem")
        destino = cleaned.get("conta_destino")
        if origem and destino and origem == destino:
            raise forms.ValidationError("A conta de origem e destino não podem ser iguais.")
        valor = cleaned.get("valor")
        if valor is not None and valor <= 0:
            raise forms.ValidationError("O valor da transferência deve ser maior que zero.")
        return cleaned


# ══════════════════════════════════════════════
# PROJEÇÃO DE FLUXO DE CAIXA
# ══════════════════════════════════════════════

class ProjecaoFluxoCaixaForm(forms.ModelForm):
    class Meta:
        model = ProjecaoFluxoCaixa
        fields = [
            "conta_bancaria", "cenario", "data_referencia",
            "entradas_previstas", "saidas_previstas", "saldo_projetado",
        ]
        widgets = {
            "conta_bancaria":     forms.Select(attrs={"class": FS}),
            "cenario":            forms.Select(attrs={"class": FS}),
            "data_referencia":    forms.DateInput(attrs={"class": FC, "type": "date"}),
            "entradas_previstas": forms.NumberInput(attrs={"class": FC, "placeholder": "0,00", "step": "0.01"}),
            "saidas_previstas":   forms.NumberInput(attrs={"class": FC, "placeholder": "0,00", "step": "0.01"}),
            "saldo_projetado":    forms.NumberInput(attrs={"class": FC, "placeholder": "0,00", "step": "0.01"}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields["conta_bancaria"].queryset = ContaBancaria.objects.filter(
                empresa=empresa, ativo=True
            )
            self.fields["cenario"].queryset = TipoCenarioFluxo.objects.filter(ativo=True)
        self.fields["conta_bancaria"].required = False

    def clean(self):
        cleaned = super().clean()
        entradas = cleaned.get("entradas_previstas", 0)
        saidas   = cleaned.get("saidas_previstas", 0)
        if entradas is not None and saidas is not None:
            if entradas < 0:
                self.add_error("entradas_previstas", "Entradas previstas não podem ser negativas.")
            if saidas < 0:
                self.add_error("saidas_previstas", "Saídas previstas não podem ser negativas.")
        return cleaned