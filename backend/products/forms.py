# products/forms.py
from django import forms
from .models import Product

# Bloque: Formulario de Producto con widgets Bootstrap.
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'company',
            'sku',
            'name',
            'description',
            'price',
            'cost',
            'category',
            'is_active',
        ]
        widgets = {
            'company': forms.Select(attrs={'class': 'form-select'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
            }),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
