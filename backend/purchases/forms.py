# purchases/forms.py
from django import forms
from .models import Purchase, PurchaseItem
from branches.models import Branch
from products.models import Product
from .models import Supplier
from django.utils import timezone


# Bloque: datos generales de la compra (cabecera).
class PurchaseCreateForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['branch', 'supplier', 'date']
        widgets = {
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    # Bloque: filtrado por empresa del usuario.
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and getattr(user, 'company', None):
            self.fields['branch'].queryset = Branch.objects.filter(company=user.company)
            self.fields['supplier'].queryset = Supplier.objects.filter(company=user.company)

    def clean_date(self):
        date = self.cleaned_data['date']
        if date > timezone.now().date():
            raise forms.ValidationError("La fecha no puede ser futura.")
        return date        


# Bloque: datos del ítem simple de la compra.
class PurchaseItemSimpleForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    unit_cost = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        max_digits=10,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    # Bloque: filtrado por empresa del usuario.
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and getattr(user, 'company', None):
            self.fields['product'].queryset = Product.objects.filter(company=user.company)

    def clean(self):
        if self.quantity <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor a cero.")
        if self.unit_cost <= 0:
            raise forms.ValidationError("El precio debe ser mayor a cero.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)        

from django import forms
from .models import Supplier

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        # SIN company: la seteamos en la vista con request.user.company
        fields = ['name', 'rut', 'contact_name', 'contact_email', 'contact_phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '11.111.111-1'}),
            'contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }

    # Si la vista pasa user=..., lo recibimos y lo ignoramos para no romper __init__
    def __init__(self, *args, **kwargs):
        kwargs.pop('user', None)  # evitar KeyError por kwargs inesperado
        super().__init__(*args, **kwargs)