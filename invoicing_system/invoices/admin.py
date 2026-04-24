from django.contrib import admin
from .models import Invoice, InvoiceItem, Payment

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    readonly_fields = ['amount']

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'client', 'invoice_date', 'grand_total', 'amount_paid', 'balance_due', 'status']
    list_filter = ['status', 'gst_type', 'invoice_date']
    search_fields = ['invoice_number', 'client__vendor_name']
    readonly_fields = ['invoice_number', 'invoice_sequence', 'created_at', 'updated_at']
    inlines = [InvoiceItemInline, PaymentInline]

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'payment_date', 'amount', 'mode', 'reference_no']
    list_filter = ['mode', 'payment_date']
