from django import forms
from .models import (
    SegmentoEmpresa, RegimeTributario, TipoDocumento,
    TipoContato, TipoAcaoLog, TipoNotificacao,
    Empresa, FilialEmpresa, PerfilAcesso, Usuario,
)


class SegmentoEmpresaForm(forms.ModelForm):
    class Meta:
        model = SegmentoEmpresa
        fields = ["nome", "ativo"]


class RegimeTributarioForm(forms.ModelForm):
    class Meta:
        model = RegimeTributario
        fields = ["nome", "codigo", "ativo"]


class TipoDocumentoForm(forms.ModelForm):
    class Meta:
        model = TipoDocumento
        fields = ["nome", "sigla", "mascara", "ativo"]

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


class TipoNotificacaoForm(forms.ModelForm):
    class Meta:
        model = TipoNotificacao
        fields = ["nome", "icone", "ativo"]


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
            "data_vencimento_plano": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_cnpj(self):
        cnpj = self.cleaned_data["cnpj"]
        qs = Empresa.objects.filter(cnpj=cnpj)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe uma empresa cadastrada com este CNPJ.")
        return cnpj


class FilialEmpresaForm(forms.ModelForm):
    class Meta:
        model = FilialEmpresa
        fields = [
            "nome", "cnpj",
            "cep", "logradouro", "numero",
            "cidade", "estado", "ativo",
        ]

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa


class PerfilAcessoForm(forms.ModelForm):
    class Meta:
        model = PerfilAcesso
        fields = [
            "nome", "descricao", "permissoes",
            "pode_aprovar_pagamentos", "nivel_aprovacao", "ativo",
        ]
        widgets = {
            "permissoes": forms.Textarea(attrs={"rows": 6, "class": "font-mono text-sm"}),
            "descricao": forms.Textarea(attrs={"rows": 3}),
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


class UsuarioForm(forms.ModelForm):
    password1 = forms.CharField(label="Senha", widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label="Confirmar senha", widget=forms.PasswordInput, required=False)

    class Meta:
        model = Usuario
        fields = [
            "nome", "email", "empresa_principal", "perfil_acesso",
            "telefone", "avatar", "dois_fatores_ativo", "is_active",
        ]

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

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields["perfil_acesso"].queryset = PerfilAcesso.objects.filter(
                empresa=empresa, ativo=True
            )