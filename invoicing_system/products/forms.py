from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model   = Product
        # description and category removed
        fields  = ['name', 'hsn_sac', 'unit', 'rate', 'gst_rate', 'is_service']
        widgets = {
            'name':      forms.TextInput(attrs={'class': 'form-control'}),
            'hsn_sac':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'HSN/SAC Code'}),
            'unit':      forms.Select(attrs={'class': 'form-select'}),
            'rate':      forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'gst_rate':  forms.Select(attrs={'class': 'form-select'}),
            'is_service':forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
