from django import forms
from .models import (
    TipoPessoa, CategoriaFornecedor, CategoriaCliente,
    TipoConta, TipoChavePix, TipoPlanoContas, TipoCentroCusto,
    Fornecedor, ContatoFornecedor,
    Cliente, ContatoCliente,
    ContaBancaria,
    PlanoContas, CentroCusto,
)
from apps.authentication.models import TipoContato


# ══════════════════════════════════════════════
# TABELAS DE DOMÍNIO
# ══════════════════════════════════════════════

class TipoPessoaForm(forms.ModelForm):
    class Meta:
        model = TipoPessoa
        fields = ["nome", "ativo"]

    def clean_nome(self):
        nome = self.cleaned_data["nome"]
        qs = TipoPessoa.objects.filter(nome__iexact=nome)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe um tipo de pessoa com este nome.")
        return nome


class CategoriaFornecedorForm(forms.ModelForm):
    class Meta:
        model = CategoriaFornecedor
        fields = ["nome", "descricao", "ativo"]
        widgets = {"descricao": forms.Textarea(attrs={"rows": 2})}

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa

    def clean_nome(self):
        nome = self.cleaned_data["nome"]
        qs = CategoriaFornecedor.objects.filter(empresa=self.empresa, nome__iexact=nome)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe uma categoria com este nome.")
        return nome


class CategoriaClienteForm(forms.ModelForm):
    class Meta:
        model = CategoriaCliente
        fields = ["nome", "descricao", "ativo"]
        widgets = {"descricao": forms.Textarea(attrs={"rows": 2})}

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa

    def clean_nome(self):
        nome = self.cleaned_data["nome"]
        qs = CategoriaCliente.objects.filter(empresa=self.empresa, nome__iexact=nome)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe uma categoria com este nome.")
        return nome


class TipoContaForm(forms.ModelForm):
    class Meta:
        model = TipoConta
        fields = ["nome", "ativo"]

    def clean_nome(self):
        nome = self.cleaned_data["nome"]
        qs = TipoConta.objects.filter(nome__iexact=nome)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe um tipo de conta com este nome.")
        return nome


class TipoChavePixForm(forms.ModelForm):
    class Meta:
        model = TipoChavePix
        fields = ["nome", "ativo"]

    def clean_nome(self):
        nome = self.cleaned_data["nome"]
        qs = TipoChavePix.objects.filter(nome__iexact=nome)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe um tipo de chave PIX com este nome.")
        return nome


class TipoPlanoContasForm(forms.ModelForm):
    class Meta:
        model = TipoPlanoContas
        fields = ["nome", "natureza", "ativo"]

    def clean_nome(self):
        nome = self.cleaned_data["nome"]
        qs = TipoPlanoContas.objects.filter(nome__iexact=nome)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe um tipo de plano de contas com este nome.")
        return nome


class TipoCentroCustoForm(forms.ModelForm):
    class Meta:
        model = TipoCentroCusto
        fields = ["nome", "ativo"]

    def clean_nome(self):
        nome = self.cleaned_data["nome"]
        qs = TipoCentroCusto.objects.filter(nome__iexact=nome)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe um tipo de centro de custo com este nome.")
        return nome


# ══════════════════════════════════════════════
# FORNECEDORES
# ══════════════════════════════════════════════

class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = [
            "tipo_pessoa", "categoria", "razao_social", "nome_fantasia",
            "cpf_cnpj", "inscricao_estadual", "inscricao_municipal",
            "cep", "logradouro", "numero", "complemento",
            "bairro", "cidade", "estado", "pais",
            "prazo_padrao_pagamento", "limite_credito",
            "observacoes", "ativo",
        ]
        widgets = {
            "observacoes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa
        if empresa:
            self.fields["categoria"].queryset = CategoriaFornecedor.objects.filter(
                empresa=empresa, ativo=True
            )

    def clean_cpf_cnpj(self):
        cpf_cnpj = self.cleaned_data["cpf_cnpj"]
        qs = Fornecedor.objects.filter(empresa=self.empresa, cpf_cnpj=cpf_cnpj)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                "Já existe um fornecedor com este CPF/CNPJ nesta empresa."
            )
        return cpf_cnpj


class ContatoFornecedorForm(forms.ModelForm):
    class Meta:
        model = ContatoFornecedor
        fields = ["tipo", "valor", "responsavel", "principal"]

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields["tipo"].queryset = TipoContato.objects.filter(
                empresa=empresa, ativo=True
            )


# ══════════════════════════════════════════════
# CLIENTES
# ══════════════════════════════════════════════

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            "tipo_pessoa", "categoria", "razao_social", "nome_fantasia",
            "cpf_cnpj", "inscricao_estadual", "data_nascimento",
            "cep", "logradouro", "numero", "complemento",
            "bairro", "cidade", "estado", "pais",
            "limite_credito", "prazo_padrao_recebimento",
            "score_credito", "inadimplente",
            "observacoes", "ativo",
        ]
        widgets = {
            "data_nascimento": forms.DateInput(attrs={"type": "date"}),
            "observacoes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa
        if empresa:
            self.fields["categoria"].queryset = CategoriaCliente.objects.filter(
                empresa=empresa, ativo=True
            )

    def clean_cpf_cnpj(self):
        cpf_cnpj = self.cleaned_data["cpf_cnpj"]
        qs = Cliente.objects.filter(empresa=self.empresa, cpf_cnpj=cpf_cnpj)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                "Já existe um cliente com este CPF/CNPJ nesta empresa."
            )
        return cpf_cnpj


class ContatoClienteForm(forms.ModelForm):
    class Meta:
        model = ContatoCliente
        fields = ["tipo", "valor", "responsavel", "principal"]

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields["tipo"].queryset = TipoContato.objects.filter(
                empresa=empresa, ativo=True
            )


# ══════════════════════════════════════════════
# CONTAS BANCÁRIAS
# ══════════════════════════════════════════════

class ContaBancariaForm(forms.ModelForm):
    class Meta:
        model = ContaBancaria
        fields = [
            "banco", "filial", "tipo_conta", "nome",
            "agencia", "agencia_dv", "conta", "conta_dv",
            "convenio", "carteira",
            "saldo_inicial", "data_saldo_inicial",
            "chave_pix", "tipo_chave_pix",
            "ativo",
        ]
        widgets = {
            "data_saldo_inicial": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            from apps.authentication.models import FilialEmpresa
            self.fields["filial"].queryset = FilialEmpresa.objects.filter(
                empresa=empresa, ativo=True
            )
            self.fields["filial"].required = False


# ══════════════════════════════════════════════
# PLANO DE CONTAS
# ══════════════════════════════════════════════

class PlanoContasForm(forms.ModelForm):
    class Meta:
        model = PlanoContas
        fields = [
            "tipo", "codigo", "nome", "descricao",
            "conta_pai", "nivel",
            "analitica", "aceita_lancamentos", "ativo",
        ]
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa
        if empresa:
            self.fields["conta_pai"].queryset = PlanoContas.objects.filter(
                empresa=empresa, analitica=False, ativo=True
            ).order_by("codigo")
            self.fields["conta_pai"].required = False

    def clean_codigo(self):
        codigo = self.cleaned_data["codigo"]
        qs = PlanoContas.objects.filter(empresa=self.empresa, codigo=codigo)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe uma conta com este código nesta empresa.")
        return codigo


# ══════════════════════════════════════════════
# CENTRO DE CUSTO
# ══════════════════════════════════════════════

class CentroCustoForm(forms.ModelForm):
    class Meta:
        model = CentroCusto
        fields = [
            "tipo", "codigo", "nome", "descricao",
            "responsavel", "centro_pai", "ativo",
        ]
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa
        if empresa:
            self.fields["centro_pai"].queryset = CentroCusto.objects.filter(
                empresa=empresa, ativo=True
            ).order_by("codigo")
            self.fields["centro_pai"].required = False

    def clean_codigo(self):
        codigo = self.cleaned_data["codigo"]
        qs = CentroCusto.objects.filter(empresa=self.empresa, codigo=codigo)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                "Já existe um centro de custo com este código nesta empresa."
            )
        return codigo