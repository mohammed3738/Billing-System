from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['client_code', 'vendor_name', 'gst_no', 'billing_city', 'billing_state', 'payment_terms', 'is_active']
    list_filter = ['billing_state', 'payment_terms', 'is_active']
    search_fields = ['client_code', 'vendor_name', 'gst_no']
    readonly_fields = ['client_code', 'created_at', 'updated_at']
