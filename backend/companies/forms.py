from django import forms
from .models import Company, Subscription

# Bloque: formulario básico de empresa (para super_admin).
class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        # SOLO campos que EXISTEN en tu modelo Company
        fields = ['name', 'rut']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
        }


# Bloque: formulario de suscripción (plan y fechas).
class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['plan_name', 'start_date', 'end_date', 'active']
        widgets = {
            'plan_name': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
