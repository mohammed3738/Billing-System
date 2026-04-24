from django.contrib import admin
from .models import Quotation, QuotationItem


class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 0
    readonly_fields = ['amount']


# class QuotationPaymentInline(admin.TabularInline):
#     model = QuotationPayment
#     extra = 0

admin.site.register(Quotation)

# class QuotationAdmin(admin.ModelAdmin):
#     list_display = ['quotation_number', 'client', 'quotation_date', 'grand_total', 'amount_paid', 'balance_due', 'status']
#     list_filter = ['status', 'gst_type', 'quotation_date']
#     search_fields = ['quotation_number', 'client__vendor_name']
#     readonly_fields = ['quotation_number', 'quotation_sequence', 'created_at', 'updated_at']
#     inlines = [QuotationItemInline]


# @admin.register(QuotationPayment)
# class QuotationPaymentAdmin(admin.ModelAdmin):
#     list_display = ['quotation', 'payment_date', 'amount', 'mode', 'reference_no']
#     list_filter = ['mode', 'payment_date']

