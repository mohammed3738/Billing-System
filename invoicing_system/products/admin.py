from django.contrib import admin
from .models import Product

# @admin.register(ProductCategory)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'hsn_sac', 'unit', 'rate', 'gst_rate', 'is_service', 'is_active']
    list_filter = ['gst_rate', 'unit', 'is_service', 'is_active']
    search_fields = ['name', 'hsn_sac']
