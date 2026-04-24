from django import forms
from .models import Client, STATE_CHOICES, PAYMENT_TERMS

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        exclude = ['client_code', 'created_at', 'updated_at', 'is_active']
        widgets = {
            'vendor_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter company/person name'}),
            'gst_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'GST Number'}),
            'payment_terms': forms.Select(attrs={'class': 'form-select'}),
            'term_in_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'billing_address1': forms.TextInput(attrs={'class': 'form-control'}),
            'billing_address2': forms.TextInput(attrs={'class': 'form-control'}),
            'billing_city': forms.TextInput(attrs={'class': 'form-control'}),
            'billing_pin': forms.TextInput(attrs={'class': 'form-control'}),
            'billing_state': forms.Select(attrs={'class': 'form-select'}),
            'billing_country': forms.TextInput(attrs={'class': 'form-control'}),
            'billing_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'billing_contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'billing_contact_no': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_name': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_address1': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_address2': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_city': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_pin': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_state': forms.Select(attrs={'class': 'form-select'}),
            'shipping_country': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_contact_no': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91XXXXXXXXXX'}),
        }
