from django import forms
from .models import Invoice, Payment, GST_TYPE_CHOICES, PAYMENT_MODE

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['client', 'invoice_date', 'due_date', 'gst_type',
                  'buyer_order_no', 'dispatch_through', 'terms_conditions', 'notes']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'invoice_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gst_type': forms.Select(attrs={'class': 'form-select'}),
            'buyer_order_no': forms.TextInput(attrs={'class': 'form-control'}),
            'dispatch_through': forms.TextInput(attrs={'class': 'form-control'}),
            'terms_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_date', 'amount', 'mode', 'reference_no', 'notes']
        widgets = {
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'mode': forms.Select(attrs={'class': 'form-select'}),
            'reference_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cheque/UTR/Ref No.'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
