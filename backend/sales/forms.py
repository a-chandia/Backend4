# sales/forms.py
from django import forms
from branches.models import Branch
from products.models import Product
from .models import Sale

class SaleCreateForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['branch', 'payment_method']
        widgets = {
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and getattr(user, 'company', None):
            self.fields['branch'].queryset = Branch.objects.filter(company=user.company)

            if user.role == 'vendedor':
                if user.default_branch:
                    self.fields['branch'].initial = user.default_branch
                    self.fields['branch'].widget = forms.HiddenInput()
                else:
                    self.fields['branch'].queryset = Branch.objects.none()


class SaleItemSimpleForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_product'})
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_quantity'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and getattr(user, 'company', None):
            self.fields['product'].queryset = Product.objects.filter(company=user.company)
