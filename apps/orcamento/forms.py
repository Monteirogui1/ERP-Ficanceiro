from django import forms
from .models import StatusOrcamento, Orcamento, ItemOrcamento
from apps.sistema.models import PlanoContas, CentroCusto
from apps.authentication.models import Usuario


class StatusOrcamentoForm(forms.ModelForm):
    class Meta:
        model = StatusOrcamento
        fields = ["nome", "ativo"]

    def clean_nome(self):
        nome = self.cleaned_data["nome"]
        qs = StatusOrcamento.objects.filter(nome__iexact=nome)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe um status com este nome.")
        return nome


class OrcamentoForm(forms.ModelForm):
    class Meta:
        model = Orcamento
        fields = ["nome", "descricao", "ano", "status", "aprovado_por", "data_aprovacao"]
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 3}),
            "data_aprovacao": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa
        self.fields["status"].queryset = StatusOrcamento.objects.filter(ativo=True)
        if empresa:
            self.fields["aprovado_por"].queryset = Usuario.objects.filter(
                empresas_acesso__empresa=empresa,
                empresas_acesso__ativo=True,
                is_active=True,
            ).distinct()
        for f in ["descricao", "aprovado_por", "data_aprovacao"]:
            self.fields[f].required = False

    def clean(self):
        cleaned = super().clean()
        nome = cleaned.get("nome")
        ano = cleaned.get("ano")
        if nome and ano and self.empresa:
            qs = Orcamento.objects.filter(empresa=self.empresa, nome__iexact=nome, ano=ano)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(
                    f"Já existe um orçamento com este nome para o ano {ano}."
                )
        return cleaned


class ItemOrcamentoForm(forms.ModelForm):
    class Meta:
        model = ItemOrcamento
        fields = [
            "plano_contas", "centro_custo", "mes",
            "valor_previsto", "valor_revisado", "observacoes",
        ]
        widgets = {
            "observacoes": forms.Textarea(attrs={"rows": 2}),
            "mes": forms.Select(choices=[
                (1, "Janeiro"), (2, "Fevereiro"), (3, "Março"),
                (4, "Abril"), (5, "Maio"), (6, "Junho"),
                (7, "Julho"), (8, "Agosto"), (9, "Setembro"),
                (10, "Outubro"), (11, "Novembro"), (12, "Dezembro"),
            ]),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa
        if empresa:
            self.fields["plano_contas"].queryset = PlanoContas.objects.filter(
                empresa=empresa, analitica=True, ativo=True
            ).order_by("codigo")
            self.fields["centro_custo"].queryset = CentroCusto.objects.filter(
                empresa=empresa, ativo=True
            ).order_by("codigo")
        for f in ["centro_custo", "valor_revisado", "observacoes"]:
            self.fields[f].required = False

    def clean_valor_previsto(self):
        valor = self.cleaned_data["valor_previsto"]
        if valor < 0:
            raise forms.ValidationError("O valor previsto não pode ser negativo.")
        return valor