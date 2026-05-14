from django import forms
from .models import TaxReturn, RETURN_TYPE_CHOICES, FREQUENCY_CHOICES, STATUS_CHOICES, MONTH_CHOICES

YEAR_CHOICES = [(y, str(y)) for y in range(2020, 2031)]

class TaxReturnForm(forms.ModelForm):
    class Meta:
        model = TaxReturn
        exclude = ['company', 'created_at', 'updated_at']
        widgets = {
            'return_type':   forms.Select(attrs={'class': 'form-select', 'id': 'id_return_type'}),
            'frequency':     forms.Select(attrs={'class': 'form-select', 'id': 'id_frequency'}),
            'month':         forms.Select(attrs={'class': 'form-select'}),
            'year':          forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2026'}),
            'from_date':     forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'to_date':       forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'return_period': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. April 2026, Q1 FY 2026-27'}),
            'due_date':      forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'filed_date':    forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status':        forms.Select(attrs={'class': 'form-select'}),
            'computation_file':  forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'return_filed_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'notes':         forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional notes'}),
        }
