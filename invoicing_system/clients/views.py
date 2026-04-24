from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Client
from .forms import ClientForm
from core.tenancy import company_required, admin_required, get_company
import json

@company_required
def client_list(request):
    company = get_company(request.user)
    q = request.GET.get('q', '')
    clients = Client.objects.filter(company=company, is_active=True)
    if q:
        clients = clients.filter(Q(vendor_name__icontains=q)|Q(client_code__icontains=q)|Q(gst_no__icontains=q))
    return render(request, 'clients/list.html', {'clients': clients, 'q': q})

@company_required
def client_create(request):
    company = get_company(request.user)
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.company = company
            client.save()
            messages.success(request, f'Client {client.client_code} created!')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'id': client.id, 'code': client.client_code, 'name': client.vendor_name})
            return redirect('clients:list')
    else:
        form = ClientForm()
    return render(request, 'clients/form.html', {'form': form, 'title': 'Add New Client'})

@company_required
def client_edit(request, pk):
    company = get_company(request.user)
    client = get_object_or_404(Client, pk=pk, company=company)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client updated!')
            return redirect('clients:list')
    else:
        form = ClientForm(instance=client)
    return render(request, 'clients/form.html', {'form': form, 'title': f'Edit {client.vendor_name}', 'client': client})

@company_required
def client_detail(request, pk):
    company = get_company(request.user)
    client = get_object_or_404(Client, pk=pk, company=company)
    invoices = client.invoices.all().order_by('-invoice_date')[:10]
    return render(request, 'clients/detail.html', {'client': client, 'invoices': invoices})

@company_required
def client_delete(request, pk):
    company = get_company(request.user)
    client = get_object_or_404(Client, pk=pk, company=company)
    if request.method == 'POST':
        client.is_active = False
        client.save()
        messages.success(request, 'Client deactivated.')
        return redirect('clients:list')
    return render(request, 'clients/confirm_delete.html', {'client': client})

@company_required
def client_get_or_create(request):
    company = get_company(request.user)
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('vendor_name', '').strip()
        if not name:
            return JsonResponse({'error': 'Name required'}, status=400)
        qs = Client.objects.filter(company=company, vendor_name__iexact=name)
        if qs.exists():
            client = qs.first()
            created = False
        else:
            client = Client.objects.create(company=company, vendor_name=name)
            created = True
        return JsonResponse({'id': client.id, 'client_code': client.client_code,
            'vendor_name': client.vendor_name, 'gst_no': client.gst_no or '',
            'billing_address1': client.billing_address1, 'billing_city': client.billing_city,
            'billing_state': client.billing_state, 'billing_pin': client.billing_pin,
            'whatsapp_number': client.whatsapp_number, 'created': created})
    return JsonResponse({'error': 'POST required'}, status=405)

@company_required
def client_search_ajax(request):
    company = get_company(request.user)
    q = request.GET.get('q', '')
    clients = Client.objects.filter(company=company, is_active=True)
    if q:
        clients = clients.filter(Q(vendor_name__icontains=q)|Q(client_code__icontains=q))
    data = [{'id': c.id, 'text': f"{c.client_code} - {c.vendor_name}", 'code': c.client_code,
             'name': c.vendor_name, 'gst': c.gst_no or '',
             'address': c.billing_address1, 'city': c.billing_city,
             'state': c.billing_state, 'pin': c.billing_pin,
             'whatsapp': c.whatsapp_number} for c in clients[:20]]
    return JsonResponse({'results': data})

@company_required
def client_detail_ajax(request, pk):
    company = get_company(request.user)
    client = get_object_or_404(Client, pk=pk, company=company)
    return JsonResponse({
        'id': client.id, 'client_code': client.client_code,
        'vendor_name': client.vendor_name, 'gst_no': client.gst_no or '',
        'billing_address1': client.billing_address1, 'billing_address2': client.billing_address2,
        'billing_city': client.billing_city, 'billing_state': client.billing_state,
        'billing_pin': client.billing_pin, 'billing_country': client.billing_country,
        'billing_contact_person': client.billing_contact_person,
        'billing_contact_no': client.billing_contact_no, 'billing_email': client.billing_email,
        'shipping_name': client.shipping_name or client.vendor_name,
        'shipping_address1': client.shipping_address1 or client.billing_address1,
        'shipping_city': client.shipping_city or client.billing_city,
        'shipping_state': client.shipping_state or client.billing_state,
        'shipping_pin': client.shipping_pin or client.billing_pin,
        'whatsapp_number': client.whatsapp_number,
        'payment_terms': client.payment_terms, 'term_in_days': client.term_in_days,
    })
