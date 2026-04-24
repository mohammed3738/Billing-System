from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from .models import Company, CompanyUser
from .forms import CompanyForm, CompanyUserForm
from core.tenancy import admin_required, company_required, get_company, get_company_user, SUPERADMIN_COMPANY_SESSION_KEY
import json

def superadmin_required(view_func):
    """Only Django superusers (Taxporium staff) can access."""
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.conf import settings
            return redirect(settings.LOGIN_URL)
        if not request.user.is_superuser:
            messages.error(request, 'Access denied. Superadmin only.')
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return wrapper


@superadmin_required
def company_list(request):
    companies = Company.objects.filter(is_active=True).prefetch_related('users')
    return render(request, 'superadmin/company_list.html', {'companies': companies})


@superadmin_required
def company_create(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save()
            messages.success(request, f'Company "{company.name}" created!')
            return redirect('superadmin:company_detail', pk=company.pk)
    else:
        form = CompanyForm()
    return render(request, 'superadmin/company_form.html', {'form': form, 'title': 'Add Company'})


@superadmin_required
def company_edit(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company updated!')
            return redirect('superadmin:company_detail', pk=company.pk)
    else:
        form = CompanyForm(instance=company)
    return render(request, 'superadmin/company_form.html', {'form': form, 'title': f'Edit {company.name}', 'company': company})


@superadmin_required
def company_detail(request, pk):
    company = get_object_or_404(Company, pk=pk)
    company_users = company.users.select_related('user').all()
    return render(request, 'superadmin/company_detail.html', {
        'company': company,
        'company_users': company_users,
    })


@superadmin_required
def enter_company(request, pk):
    company = get_object_or_404(Company, pk=pk, is_active=True)
    request.session[SUPERADMIN_COMPANY_SESSION_KEY] = company.pk
    messages.success(request, f'Entered {company.name}.')
    target = request.GET.get('next') or 'dashboard:index'
    return redirect(target)


@superadmin_required
def exit_company(request):
    request.session.pop(SUPERADMIN_COMPANY_SESSION_KEY, None)
    messages.success(request, 'Returned to superadmin view.')
    return redirect('superadmin:company_list')


@superadmin_required
def company_delete(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        company.is_active = False
        company.save()
        messages.success(request, f'Company "{company.name}" deactivated.')
        return redirect('superadmin:company_list')
    return render(request, 'superadmin/confirm_delete.html', {'company': company})


@superadmin_required
def add_company_user(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        username   = request.POST.get('username', '').strip()
        password   = request.POST.get('password', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        email      = request.POST.get('email', '').strip()
        role       = request.POST.get('role', 'staff')

        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return redirect('superadmin:company_detail', pk=pk)

        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" already exists.')
            return redirect('superadmin:company_detail', pk=pk)

        user = User.objects.create_user(
            username=username, password=password,
            first_name=first_name, email=email
        )
        CompanyUser.objects.create(user=user, company=company, role=role)
        messages.success(request, f'User "{username}" added to {company.name} as {role}.')
    return redirect('superadmin:company_detail', pk=pk)


@superadmin_required
def remove_company_user(request, pk, user_pk):
    cu = get_object_or_404(CompanyUser, pk=user_pk, company_id=pk)
    if request.method == 'POST':
        username = cu.user.username
        cu.user.delete()          # deletes User + CompanyUser (cascade)
        messages.success(request, f'User "{username}" removed.')
    return redirect('superadmin:company_detail', pk=pk)


@superadmin_required
def change_user_role(request, pk, user_pk):
    cu = get_object_or_404(CompanyUser, pk=user_pk, company_id=pk)
    if request.method == 'POST':
        role = request.POST.get('role', 'staff')
        cu.role = role
        cu.save()
        messages.success(request, f'Role updated to {role}.')
    return redirect('superadmin:company_detail', pk=pk)


@admin_required
def tenant_user_list(request):
    company = get_company(request.user, request)
    company_users = company.users.select_related('user').all()
    return render(request, 'superadmin/tenant_user_list.html', {
        'company': company,
        'company_users': company_users,
        'self_company_user': get_company_user(request.user),
    })


@admin_required
def tenant_add_user(request):
    company = get_company(request.user, request)
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        email = request.POST.get('email', '').strip()
        role = request.POST.get('role', 'staff')

        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return redirect('superadmin:tenant_users')

        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" already exists.')
            return redirect('superadmin:tenant_users')

        user = User.objects.create_user(
            username=username, password=password,
            first_name=first_name, email=email
        )
        CompanyUser.objects.create(user=user, company=company, role=role)
        messages.success(request, f'User "{username}" added to {company.name} as {role}.')
    return redirect('superadmin:tenant_users')


@admin_required
def tenant_remove_user(request, user_pk):
    company = get_company(request.user, request)
    cu = get_object_or_404(CompanyUser, pk=user_pk, company=company)
    current_cu = get_company_user(request.user)
    if request.method == 'POST':
        if current_cu and cu.pk == current_cu.pk:
            messages.error(request, 'You cannot remove your own account.')
            return redirect('superadmin:tenant_users')
        username = cu.user.username
        cu.user.delete()
        messages.success(request, f'User "{username}" removed.')
    return redirect('superadmin:tenant_users')


@admin_required
def tenant_change_user_role(request, user_pk):
    company = get_company(request.user, request)
    cu = get_object_or_404(CompanyUser, pk=user_pk, company=company)
    current_cu = get_company_user(request.user)
    if request.method == 'POST':
        role = request.POST.get('role', 'staff')
        if current_cu and cu.pk == current_cu.pk and role != 'admin':
            messages.error(request, 'You cannot remove your own admin access.')
            return redirect('superadmin:tenant_users')
        cu.role = role
        cu.save()
        messages.success(request, f'Role updated to {role}.')
    return redirect('superadmin:tenant_users')
