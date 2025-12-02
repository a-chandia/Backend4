from django import forms
from .models import User
from companies.models import Company
from branches.models import Branch


class AdminClienteCreateForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Repetir contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    company = forms.ModelChoiceField(
        label='Empresa',
        queryset=Company.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'company']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Las contraseñas no coinciden.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'admin_cliente'
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class TenantUserCreateForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Repetir contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'default_branch']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'default_branch': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)

        # Restringir roles a gerente / vendedor
        self.fields['role'].choices = [
            ('gerente', 'Gerente'),
            ('vendedor', 'Vendedor'),
        ]

        # Restringir sucursales a las de la empresa
        if company is not None:
            self.fields['default_branch'].queryset = Branch.objects.filter(company=company)

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Las contraseñas no coinciden.')
        return cleaned

    def save(self, company, commit=True):
        user = super().save(commit=False)
        user.company = company
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user