from django import forms
from .models import (
    TipoPessoa, CategoriaFornecedor, CategoriaCliente,
    TipoConta, TipoChavePix, TipoPlanoContas, TipoCentroCusto,
    Fornecedor, ContatoFornecedor,
    Cliente, ContatoCliente,
    ContaBancaria,
    PlanoContas, CentroCusto, Banco,
)
from apps.authentication.models import TipoContato

FC = "form-control"
FS = "form-select"


# ══════════════════════════════════════════════
# TABELAS DE DOMÍNIO
# ══════════════════════════════════════════════

class TipoPessoaForm(forms.ModelForm):
    class Meta:
        model = TipoPessoa
        fields = ["nome", "ativo"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": FC, "placeholder": "Ex: Física, Jurídica, Estrangeira"}),
        }

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
        widgets = {
            "nome":      forms.TextInput(attrs={"class": FC, "placeholder": "Ex: Serviços, Materiais, Tecnologia"}),
            "descricao": forms.Textarea(attrs={"class": FC, "rows": 2, "placeholder": "Descrição da categoria"}),
        }

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
        widgets = {
            "nome":      forms.TextInput(attrs={"class": FC, "placeholder": "Ex: Pessoa Física, Pessoa Jurídica, Governo"}),
            "descricao": forms.Textarea(attrs={"class": FC, "rows": 2, "placeholder": "Descrição da categoria"}),
        }

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
        widgets = {
            "nome": forms.TextInput(attrs={"class": FC, "placeholder": "Ex: Conta Corrente, Conta Poupança, Caixa"}),
        }

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
        widgets = {
            "nome": forms.TextInput(attrs={"class": FC, "placeholder": "Ex: CPF, CNPJ, E-mail, Telefone, Aleatória"}),
        }

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
        widgets = {
            "nome":     forms.TextInput(attrs={"class": FC, "placeholder": "Ex: Receita, Despesa, Ativo, Passivo"}),
            "natureza": forms.Select(attrs={"class": FS}),
        }

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
        widgets = {
            "nome": forms.TextInput(attrs={"class": FC, "placeholder": "Ex: Departamento, Projeto, Unidade"}),
        }

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
            "tipo_pessoa":            forms.Select(attrs={"class": FS}),
            "categoria":              forms.Select(attrs={"class": FS}),
            "razao_social":           forms.TextInput(attrs={"class": FC, "placeholder": "Razão social ou nome completo"}),
            "nome_fantasia":          forms.TextInput(attrs={"class": FC, "placeholder": "Nome fantasia (opcional)"}),
            "cpf_cnpj":               forms.TextInput(attrs={"class": FC, "placeholder": "000.000.000-00 ou 00.000.000/0000-00"}),
            "inscricao_estadual":     forms.TextInput(attrs={"class": FC, "placeholder": "Inscrição estadual"}),
            "inscricao_municipal":    forms.TextInput(attrs={"class": FC, "placeholder": "Inscrição municipal"}),
            "cep":                    forms.TextInput(attrs={"class": FC, "placeholder": "00000-000"}),
            "logradouro":             forms.TextInput(attrs={"class": FC, "placeholder": "Rua, Av., etc."}),
            "numero":                 forms.TextInput(attrs={"class": FC, "placeholder": "Nº"}),
            "complemento":            forms.TextInput(attrs={"class": FC, "placeholder": "Sala, Andar, Galpão..."}),
            "bairro":                 forms.TextInput(attrs={"class": FC, "placeholder": "Bairro"}),
            "cidade":                 forms.TextInput(attrs={"class": FC, "placeholder": "Cidade"}),
            "estado":                 forms.TextInput(attrs={"class": FC, "placeholder": "UF"}),
            "pais":                   forms.TextInput(attrs={"class": FC, "placeholder": "Ex: Brasil"}),
            "prazo_padrao_pagamento": forms.NumberInput(attrs={"class": FC, "placeholder": "Ex: 30", "min": "0"}),
            "limite_credito":         forms.NumberInput(attrs={"class": FC, "placeholder": "0,00", "step": "0.01"}),
            "observacoes":            forms.Textarea(attrs={"class": FC, "rows": 3, "placeholder": "Observações sobre o fornecedor"}),
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
            raise forms.ValidationError("Já existe um fornecedor com este CPF/CNPJ nesta empresa.")
        return cpf_cnpj


class ContatoFornecedorForm(forms.ModelForm):
    class Meta:
        model = ContatoFornecedor
        fields = ["tipo", "valor", "responsavel", "principal"]
        widgets = {
            "tipo":        forms.Select(attrs={"class": FS}),
            "valor":       forms.TextInput(attrs={"class": FC, "placeholder": "Ex: (00) 00000-0000 ou email@dominio.com"}),
            "responsavel": forms.TextInput(attrs={"class": FC, "placeholder": "Nome do responsável pelo contato"}),
        }

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
            "tipo_pessoa":              forms.Select(attrs={"class": FS}),
            "categoria":                forms.Select(attrs={"class": FS}),
            "razao_social":             forms.TextInput(attrs={"class": FC, "placeholder": "Razão social ou nome completo"}),
            "nome_fantasia":            forms.TextInput(attrs={"class": FC, "placeholder": "Nome fantasia (opcional)"}),
            "cpf_cnpj":                 forms.TextInput(attrs={"class": FC, "placeholder": "000.000.000-00 ou 00.000.000/0000-00"}),
            "inscricao_estadual":       forms.TextInput(attrs={"class": FC, "placeholder": "Inscrição estadual"}),
            "data_nascimento":          forms.DateInput(attrs={"class": FC, "type": "date"}),
            "cep":                      forms.TextInput(attrs={"class": FC, "placeholder": "00000-000"}),
            "logradouro":               forms.TextInput(attrs={"class": FC, "placeholder": "Rua, Av., etc."}),
            "numero":                   forms.TextInput(attrs={"class": FC, "placeholder": "Nº"}),
            "complemento":              forms.TextInput(attrs={"class": FC, "placeholder": "Sala, Andar, Apto..."}),
            "bairro":                   forms.TextInput(attrs={"class": FC, "placeholder": "Bairro"}),
            "cidade":                   forms.TextInput(attrs={"class": FC, "placeholder": "Cidade"}),
            "estado":                   forms.TextInput(attrs={"class": FC, "placeholder": "UF"}),
            "pais":                     forms.TextInput(attrs={"class": FC, "placeholder": "Ex: Brasil"}),
            "limite_credito":           forms.NumberInput(attrs={"class": FC, "placeholder": "0,00", "step": "0.01"}),
            "prazo_padrao_recebimento": forms.NumberInput(attrs={"class": FC, "placeholder": "Ex: 30", "min": "0"}),
            "score_credito":            forms.NumberInput(attrs={"class": FC, "placeholder": "Ex: 750", "min": "0", "max": "1000"}),
            "observacoes":              forms.Textarea(attrs={"class": FC, "rows": 3, "placeholder": "Observações sobre o cliente"}),
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
            raise forms.ValidationError("Já existe um cliente com este CPF/CNPJ nesta empresa.")
        return cpf_cnpj


class ContatoClienteForm(forms.ModelForm):
    class Meta:
        model = ContatoCliente
        fields = ["tipo", "valor", "responsavel", "principal"]
        widgets = {
            "tipo":        forms.Select(attrs={"class": FS}),
            "valor":       forms.TextInput(attrs={"class": FC, "placeholder": "Ex: (00) 00000-0000 ou email@dominio.com"}),
            "responsavel": forms.TextInput(attrs={"class": FC, "placeholder": "Nome do responsável pelo contato"}),
        }

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
            "banco":              forms.Select(attrs={"class": FS}),
            "filial":             forms.Select(attrs={"class": FS}),
            "tipo_conta":         forms.Select(attrs={"class": FS}),
            "nome":               forms.TextInput(attrs={"class": FC, "placeholder": "Ex: Conta Principal, Conta Cobrança"}),
            "agencia":            forms.TextInput(attrs={"class": FC, "placeholder": "Número da agência"}),
            "agencia_dv":         forms.TextInput(attrs={"class": FC, "placeholder": "DV"}),
            "conta":              forms.TextInput(attrs={"class": FC, "placeholder": "Número da conta"}),
            "conta_dv":           forms.TextInput(attrs={"class": FC, "placeholder": "DV"}),
            "convenio":           forms.TextInput(attrs={"class": FC, "placeholder": "Número do convênio (cobrança)"}),
            "carteira":           forms.TextInput(attrs={"class": FC, "placeholder": "Ex: 109, 17"}),
            "saldo_inicial":      forms.NumberInput(attrs={"class": FC, "placeholder": "0,00", "step": "0.01"}),
            "data_saldo_inicial": forms.DateInput(attrs={"class": FC, "type": "date"}),
            "chave_pix":          forms.TextInput(attrs={"class": FC, "placeholder": "Chave PIX cadastrada"}),
            "tipo_chave_pix":     forms.Select(attrs={"class": FS}),
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
            "tipo":      forms.Select(attrs={"class": FS}),
            "codigo":    forms.TextInput(attrs={"class": FC, "placeholder": "Ex: 1.1.01.001"}),
            "nome":      forms.TextInput(attrs={"class": FC, "placeholder": "Nome da conta contábil"}),
            "descricao": forms.Textarea(attrs={"class": FC, "rows": 2, "placeholder": "Descrição ou observação sobre a conta"}),
            "conta_pai": forms.Select(attrs={"class": FS}),
            "nivel":     forms.NumberInput(attrs={"class": FC, "placeholder": "Ex: 1, 2, 3", "min": "1"}),
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
            "tipo":        forms.Select(attrs={"class": FS}),
            "codigo":      forms.TextInput(attrs={"class": FC, "placeholder": "Ex: CC-001, TI-02"}),
            "nome":        forms.TextInput(attrs={"class": FC, "placeholder": "Nome do centro de custo"}),
            "descricao":   forms.Textarea(attrs={"class": FC, "rows": 2, "placeholder": "Descrição ou responsabilidade do centro"}),
            "responsavel": forms.TextInput(attrs={"class": FC, "placeholder": "Nome do responsável"}),
            "centro_pai":  forms.Select(attrs={"class": FS}),
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
            raise forms.ValidationError("Já existe um centro de custo com este código nesta empresa.")
        return codigo

class BancoForm(forms.ModelForm):
    class Meta:
        model = Banco
        fields = ["codigo", "nome", "ispb", "ativo"]
        widgets = {
            "codigo": forms.TextInput(attrs={"class": FC, "placeholder": "Ex: 001, 033, 341"}),
            "nome":   forms.TextInput(attrs={"class": FC, "placeholder": "Nome do banco"}),
            "ispb":   forms.TextInput(attrs={"class": FC, "placeholder": "8 dígitos — opcional"}),
        }

    def clean_codigo(self):
        codigo = self.cleaned_data["codigo"]
        qs = Banco.objects.filter(codigo=codigo)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe um banco com este código.")
        return codigo