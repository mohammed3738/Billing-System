"""
tenancy.py — helpers to get the current company and enforce data isolation.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from superadmin.models import Company


SUPERADMIN_COMPANY_SESSION_KEY = 'superadmin_company_id'


def get_company(user, request=None):
    """
    Return the Company for a regular user (via CompanyUser).
    Superusers can work inside a selected company context.
    """
    active_company = getattr(user, '_active_company', None)
    if active_company is not None:
        return active_company
    if user.is_superuser:
        if request:
            company_id = request.session.get(SUPERADMIN_COMPANY_SESSION_KEY)
            if company_id:
                return Company.objects.filter(pk=company_id, is_active=True).first()
        return None
    try:
        return user.company_user.company
    except Exception:
        return None


def get_company_user(user):
    """Return CompanyUser or None."""
    try:
        return user.company_user
    except Exception:
        return None


def company_required(view_func):
    """Decorator: user must belong to a company (not just be a superuser)."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        company = get_company(request.user, request)
        if not company:
            if request.user.is_superuser:
                messages.error(request, 'Select a company first to view tenant data.')
                return redirect('superadmin:company_list')
            messages.error(request, 'Your account is not linked to any company. Contact your administrator.')
            return redirect('login')
        if not company.is_active:
            messages.error(request, 'Your company account is inactive. Contact Taxporium support.')
            return redirect('login')
        request.user._active_company = company
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Decorator: user must be company admin (not just staff)."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.is_superuser:
            company = get_company(request.user, request)
            if not company:
                messages.error(request, 'Select a company first.')
                return redirect('superadmin:company_list')
            request.user._active_company = company
            return view_func(request, *args, **kwargs)
        cu = get_company_user(request.user)
        if not cu or cu.role != 'admin':
            messages.error(request, 'Admin access required.')
            return redirect('invoices:list')
        return view_func(request, *args, **kwargs)
    return wrapper
