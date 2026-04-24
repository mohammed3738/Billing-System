from django.contrib import admin
from .models import Company, CompanyUser

class CompanyUserInline(admin.TabularInline):
    model = CompanyUser
    extra = 0

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'gst_no', 'email', 'is_active', 'created_at']
    search_fields = ['name', 'gst_no']
    inlines = [CompanyUserInline]

@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'role']
    list_filter = ['role', 'company']
