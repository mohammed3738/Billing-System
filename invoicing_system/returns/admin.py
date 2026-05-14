from django.contrib import admin
from .models import TaxReturn

@admin.register(TaxReturn)
class TaxReturnAdmin(admin.ModelAdmin):
    list_display = ['return_type', 'return_period', 'year', 'month', 'status', 'company', 'filed_date']
    list_filter  = ['return_type', 'status', 'year', 'company']
    search_fields = ['return_type', 'return_period', 'notes']
