from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Case, When, Value, IntegerField
from .models import Product
from .forms import ProductForm
from core.tenancy import company_required, admin_required, get_company
import json

@company_required
def product_list(request):
    company = get_company(request.user)
    q = request.GET.get('q', '')
    products = Product.objects.filter(company=company, is_active=True)
    if q:
        products = products.filter(Q(name__icontains=q)|Q(hsn_sac__icontains=q))
    return render(request, 'products/list.html', {'products': products, 'q': q})

@company_required
def product_create(request):
    company = get_company(request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.company = company
            product.save()
            messages.success(request, f'Product "{product.name}" created!')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'id': product.id, 'name': product.name,
                    'rate': str(product.rate), 'hsn': product.hsn_sac,
                    'gst_rate': product.gst_rate, 'unit': product.unit})
            return redirect('products:list')
    else:
        form = ProductForm()
    return render(request, 'products/form.html', {'form': form, 'title': 'Add Product'})

@company_required
def product_edit(request, pk):
    company = get_company(request.user)
    product = get_object_or_404(Product, pk=pk, company=company)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated!')
            return redirect('products:list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/form.html', {'form': form, 'title': f'Edit {product.name}'})

@company_required
def product_delete(request, pk):
    company = get_company(request.user)
    product = get_object_or_404(Product, pk=pk, company=company)
    if request.method == 'POST':
        product.is_active = False
        product.save()
        messages.success(request, 'Product removed.')
        return redirect('products:list')
    return render(request, 'products/confirm_delete.html', {'product': product})

@company_required
def product_search_ajax(request):
    company = get_company(request.user)
    q = request.GET.get('q', '')
    products = Product.objects.filter(company=company, is_active=True)
    if q:
        products = products.filter(Q(name__icontains=q)|Q(hsn_sac__icontains=q)).annotate(
            match_priority=Case(
                When(name__iexact=q, then=Value(0)),
                When(name__istartswith=q, then=Value(1)),
                When(hsn_sac__istartswith=q, then=Value(2)),
                default=Value(3),
                output_field=IntegerField(),
            )
        ).order_by('match_priority', 'name')
    data = [{'id': p.id, 'name': p.name, 'hsn_sac': p.hsn_sac,
             'rate': str(p.rate), 'unit': p.unit, 'gst_rate': p.gst_rate, 'text': p.name}
            for p in products[:20]]
    return JsonResponse({'results': data})

@company_required
def product_get_or_create(request):
    company = get_company(request.user)
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        if not name:
            return JsonResponse({'error': 'Name required'}, status=400)
        qs = Product.objects.filter(company=company, name__iexact=name)
        if qs.exists():
            product = qs.first()
            created = False
        else:
            product = Product.objects.create(
                company=company, name=name,
                rate=data.get('rate', 0),
                hsn_sac=data.get('hsn_sac', ''),
                gst_rate=data.get('gst_rate', 18),
                unit=data.get('unit', 'Nos'),
            )
            created = True
        return JsonResponse({'id': product.id, 'name': product.name, 'rate': str(product.rate),
            'hsn_sac': product.hsn_sac, 'gst_rate': product.gst_rate,
            'unit': product.unit, 'created': created})
    return JsonResponse({'error': 'POST required'}, status=405)
