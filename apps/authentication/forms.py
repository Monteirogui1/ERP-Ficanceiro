from django import forms
from .models import (
    SegmentoEmpresa, RegimeTributario, TipoDocumento,
    TipoContato, TipoAcaoLog, TipoNotificacao,
    Empresa, FilialEmpresa, PerfilAcesso, Usuario,
)

FC = "form-control"
FS = "form-select"


# ══════════════════════════════════════════════
# TABELAS DE DOMÍNIO
# ══════════════════════════════════════════════

class SegmentoEmpresaForm(forms.ModelForm):
    class Meta:
        model = SegmentoEmpresa
        fields = ["nome", "ativo"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": FC, "placeholder": "Ex: Comércio, Serviços, Indústria"}),
        }


class RegimeTributarioForm(forms.ModelForm):
    class Meta:
        model = RegimeTributario
        fields = ["nome", "codigo", "ativo"]
        widgets = {
            "nome":   forms.TextInput(attrs={"class": FC, "placeholder": "Nome do regime"}),
            "codigo": forms.TextInput(attrs={"class": FC, "placeholder": "Ex: SN, LP, LR"}),
        }


class TipoDocumentoForm(forms.ModelForm):
    class Meta:
        model = TipoDocumento
        fields = ["nome", "sigla", "mascara", "ativo"]
        widgets = {
            "nome":    forms.TextInput(attrs={"class": FC, "placeholder": "Ex: Nota Fiscal, Contrato"}),
            "sigla":   forms.TextInput(attrs={"class": FC, "placeholder": "Ex: NF, CT"}),
            "mascara": forms.TextInput(attrs={"class": FC, "placeholder": "Ex: 000.000.000-00"}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa

    def clean_sigla(self):
        sigla = self.cleaned_data["sigla"]
        qs = TipoDocumento.objects.filter(empresa=self.empresa, sigla__iexact=sigla)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe um tipo de documento com esta sigla.")
        return sigla


class TipoContatoForm(forms.ModelForm):
    class Meta:
        model = TipoContato
        fields = ["nome", "ativo"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": FC, "placeholder": "Ex: Telefone, WhatsApp, E-mail"}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa

    def clean_nome(self):
        nome = self.cleaned_data["nome"]
        qs = TipoContato.objects.filter(empresa=self.empresa, nome__iexact=nome)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe um tipo de contato com este nome.")
        return nome


class TipoAcaoLogForm(forms.ModelForm):
    class Meta:
        model = TipoAcaoLog
        fields = ["nome", "descricao"]
        widgets = {
            "nome":      forms.TextInput(attrs={"class": FC, "placeholder": "Ex: Criação, Edição, Exclusão"}),
            "descricao": forms.Textarea(attrs={"class": FC, "rows": 2, "placeholder": "Descrição da ação"}),
        }


class TipoNotificacaoForm(forms.ModelForm):
    class Meta:
        model = TipoNotificacao
        fields = ["nome", "icone", "ativo"]
        widgets = {
            "nome":  forms.TextInput(attrs={"class": FC, "placeholder": "Ex: Alerta, Aviso, Informação"}),
            "icone": forms.TextInput(attrs={"class": FC, "placeholder": "Ex: bi-bell, bi-exclamation-triangle"}),
        }


# ══════════════════════════════════════════════
# EMPRESA
# ══════════════════════════════════════════════

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = [
            "razao_social", "nome_fantasia", "cnpj",
            "inscricao_estadual", "inscricao_municipal",
            "segmento", "regime_tributario",
            "cep", "logradouro", "numero", "complemento",
            "bairro", "cidade", "estado",
            "telefone", "email", "site",
            "plano", "data_vencimento_plano", "logo", "ativo",
        ]
        widgets = {
            "razao_social":          forms.TextInput(attrs={"class": FC, "placeholder": "Razão social da empresa"}),
            "nome_fantasia":         forms.TextInput(attrs={"class": FC, "placeholder": "Nome fantasia"}),
            "cnpj":                  forms.TextInput(attrs={"class": FC, "placeholder": "00.000.000/0000-00"}),
            "inscricao_estadual":    forms.TextInput(attrs={"class": FC, "placeholder": "Inscrição estadual"}),
            "inscricao_municipal":   forms.TextInput(attrs={"class": FC, "placeholder": "Inscrição municipal"}),
            "segmento":              forms.Select(attrs={"class": FS}),
            "regime_tributario":     forms.Select(attrs={"class": FS}),
            "cep":                   forms.TextInput(attrs={"class": FC, "placeholder": "00000-000"}),
            "logradouro":            forms.TextInput(attrs={"class": FC, "placeholder": "Rua, Av., etc."}),
            "numero":                forms.TextInput(attrs={"class": FC, "placeholder": "Nº"}),
            "complemento":           forms.TextInput(attrs={"class": FC, "placeholder": "Sala, Andar, etc."}),
            "bairro":                forms.TextInput(attrs={"class": FC, "placeholder": "Bairro"}),
            "cidade":                forms.TextInput(attrs={"class": FC, "placeholder": "Cidade"}),
            "estado":                forms.TextInput(attrs={"class": FC, "placeholder": "UF"}),
            "telefone":              forms.TextInput(attrs={"class": FC, "placeholder": "(00) 00000-0000"}),
            "email":                 forms.EmailInput(attrs={"class": FC, "placeholder": "contato@empresa.com.br"}),
            "site":                  forms.URLInput(attrs={"class": FC, "placeholder": "https://www.empresa.com.br"}),
            "plano":                 forms.TextInput(attrs={"class": FC, "placeholder": "Ex: Basic, Pro, Enterprise"}),
            "data_vencimento_plano": forms.DateInput(attrs={"class": FC, "type": "date"}),
        }

    def clean_cnpj(self):
        cnpj = self.cleaned_data["cnpj"]
        qs = Empresa.objects.filter(cnpj=cnpj)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe uma empresa cadastrada com este CNPJ.")
        return cnpj


# ══════════════════════════════════════════════
# FILIAL
# ══════════════════════════════════════════════

class FilialEmpresaForm(forms.ModelForm):
    class Meta:
        model = FilialEmpresa
        fields = [
            "nome", "cnpj",
            "cep", "logradouro", "numero",
            "cidade", "estado", "ativo",
        ]
        widgets = {
            "nome":       forms.TextInput(attrs={"class": FC, "placeholder": "Nome da filial"}),
            "cnpj":       forms.TextInput(attrs={"class": FC, "placeholder": "00.000.000/0000-00"}),
            "cep":        forms.TextInput(attrs={"class": FC, "placeholder": "00000-000"}),
            "logradouro": forms.TextInput(attrs={"class": FC, "placeholder": "Rua, Av., etc."}),
            "numero":     forms.TextInput(attrs={"class": FC, "placeholder": "Nº"}),
            "cidade":     forms.TextInput(attrs={"class": FC, "placeholder": "Cidade"}),
            "estado":     forms.TextInput(attrs={"class": FC, "placeholder": "UF"}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa


# ══════════════════════════════════════════════
# PERFIL DE ACESSO
# ══════════════════════════════════════════════

class PerfilAcessoForm(forms.ModelForm):
    class Meta:
        model = PerfilAcesso
        fields = [
            "nome", "descricao", "permissoes",
            "pode_aprovar_pagamentos", "nivel_aprovacao", "ativo",
        ]
        widgets = {
            "nome":             forms.TextInput(attrs={"class": FC, "placeholder": "Ex: Financeiro, Gerente, Analista"}),
            "descricao":        forms.Textarea(attrs={"class": FC, "rows": 3, "placeholder": "Descreva as responsabilidades deste perfil"}),
            "permissoes":       forms.Textarea(attrs={"class": FC, "rows": 6, "style": "font-family: monospace; font-size: 13px;"}),
            "nivel_aprovacao":  forms.NumberInput(attrs={"class": FC, "min": 1, "placeholder": "Ex: 1, 2, 3"}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa

    def clean_nome(self):
        nome = self.cleaned_data["nome"]
        qs = PerfilAcesso.objects.filter(empresa=self.empresa, nome__iexact=nome)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe um perfil com este nome nesta empresa.")
        return nome


# ══════════════════════════════════════════════
# USUÁRIO
# ══════════════════════════════════════════════

class UsuarioForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Senha",
        required=False,
        widget=forms.PasswordInput(attrs={"class": FC, "placeholder": "Digite a senha"}),
    )
    password2 = forms.CharField(
        label="Confirmar senha",
        required=False,
        widget=forms.PasswordInput(attrs={"class": FC, "placeholder": "Confirme a senha"}),
    )

    class Meta:
        model = Usuario
        fields = [
            "nome", "email", "empresa_principal", "perfil_acesso",
            "telefone", "avatar", "dois_fatores_ativo", "is_active",
        ]
        widgets = {
            "nome":              forms.TextInput(attrs={"class": FC, "placeholder": "Nome completo"}),
            "email":             forms.EmailInput(attrs={"class": FC, "placeholder": "usuario@empresa.com.br"}),
            "empresa_principal": forms.Select(attrs={"class": FS}),
            "perfil_acesso":     forms.Select(attrs={"class": FS}),
            "telefone":          forms.TextInput(attrs={"class": FC, "placeholder": "(00) 00000-0000"}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields["perfil_acesso"].queryset = PerfilAcesso.objects.filter(
                empresa=empresa, ativo=True
            )

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 or p2:
            if p1 != p2:
                raise forms.ValidationError("As senhas não conferem.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class UsuarioEdicaoForm(forms.ModelForm):
    """Form de edição sem campos de senha — para atualização de perfil."""

    class Meta:
        model = Usuario
        fields = [
            "nome", "email", "perfil_acesso",
            "telefone", "avatar", "dois_fatores_ativo",
        ]
        widgets = {
            "nome":          forms.TextInput(attrs={"class": FC, "placeholder": "Nome completo"}),
            "email":         forms.EmailInput(attrs={"class": FC, "placeholder": "usuario@empresa.com.br"}),
            "perfil_acesso": forms.Select(attrs={"class": FS}),
            "telefone":      forms.TextInput(attrs={"class": FC, "placeholder": "(00) 00000-0000"}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields["perfil_acesso"].queryset = PerfilAcesso.objects.filter(
                empresa=empresa, ativo=True
            )