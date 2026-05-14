from django import forms
from django.forms import inlineformset_factory
from .models import Company, CompanyUser, CompanyDocument

class CompanyForm(forms.ModelForm):
    class Meta:
        model  = Company
        exclude = ['is_active', 'created_at']
        widgets = {
            'name':                forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Zaco Computers Pvt Ltd'}),
            'pan':                 forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PAN Number'}),
            'gst_no':              forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'GSTIN (15 chars)'}),
            'address':             forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'telephone':           forms.TextInput(attrs={'class': 'form-control'}),
            'mobile':              forms.TextInput(attrs={'class': 'form-control'}),
            'email':               forms.EmailInput(attrs={'class': 'form-control'}),
            'website':             forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://'}),
            'logo':                forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'beneficiary_name':    forms.TextInput(attrs={'class': 'form-control'}),
            'beneficiary_account': forms.TextInput(attrs={'class': 'form-control'}),
            'beneficiary_ifsc':    forms.TextInput(attrs={'class': 'form-control'}),
            'beneficiary_branch':  forms.TextInput(attrs={'class': 'form-control'}),
            'invoice_prefix':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. ZAC'}),
            'financial_year':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 26-27'}),
        }

class CompanyUserForm(forms.ModelForm):
    class Meta:
        model = CompanyUser
        fields = ['role']
        widgets = {'role': forms.Select(attrs={'class': 'form-select'})}


class CompanyDocumentForm(forms.ModelForm):
    class Meta:
        model = CompanyDocument
        fields = ['document_type', 'login_id', 'password', 'attachment', 'notes']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-select doc-type-select'}),
            'login_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'User ID / Login'}),
            'password': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
            'notes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Notes (optional)'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


CompanyDocumentFormSet = inlineformset_factory(
    Company, CompanyDocument,
    form=CompanyDocumentForm,
    extra=0,
    can_delete=True,
)
