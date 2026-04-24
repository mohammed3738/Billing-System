from urllib import request

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum
from .models import Quotation, QuotationItem
# from .forms import QuotationPaymentForm
from clients.models import Client
from products.models import Product
from core.tenancy import company_required, get_company, get_company_user
from decimal import Decimal
import json, datetime


@company_required
def quotation_list(request):
    company = get_company(request.user)
    status = request.GET.get('status', '')
    q = request.GET.get('q', '')
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    today = datetime.date.today()
    Quotation.objects.filter(company=company, due_date__lt=today)
    quotations = Quotation.objects.filter(company=company).select_related('client')
    if status:
        quotations = quotations.filter(status=status)
    if q:
        quotations = quotations.filter(Q(quotation_number__icontains=q) | Q(client__vendor_name__icontains=q))
    if date_from:
        quotations = quotations.filter(quotation_date__gte=date_from)
    if date_to:
        quotations = quotations.filter(quotation_date__lte=date_to)
    return render(request, 'quotations/list.html', {
        'quotations': quotations,
        'invoices': quotations,
        'status': status,
        'q': q,
        'date_from': date_from,
        'date_to': date_to,
    })


@company_required
def quotation_create(request):
    company = get_company(request.user)
    if request.method == 'POST':
        return _save_quotation(request, None, company)
    clients = Client.objects.filter(company=company, is_active=True)
    return render(request, 'quotations/form.html', {
        'title': 'New Quotation',
        'invoice': None,
        'clients': clients,
        'today': datetime.date.today().strftime('%Y-%m-%d'),
        'company_gst': company.gst_no or '',
    })


@company_required
def quotation_edit(request, pk):
    company = get_company(request.user)
    quotation = get_object_or_404(Quotation, pk=pk, company=company)
    cu = get_company_user(request.user)
    if cu and cu.role == 'staff' and quotation.status not in ('draft',):
        messages.error(request, 'Staff can only edit draft quotations.')
        return redirect('quotations:detail', pk=pk)
    if request.method == 'POST':
        return _save_quotation(request, quotation, company)
    clients = Client.objects.filter(company=company, is_active=True)
    items = list(quotation.items.values())
    return render(request, 'quotations/form.html', {
        'title': f'Edit {quotation.quotation_number}',
        'quotation': quotation,
        'invoice': quotation,
        'clients': clients,
        'items_json': json.dumps(items, default=str),
        'today': datetime.date.today().strftime('%Y-%m-%d'),
        'company_gst': company.gst_no or '',
    })


def _save_quotation(request, quotation, company):
    data = request.POST
    client_id = data.get('client_id')
    if not client_id:
        messages.error(request, 'Please select a client.')
        return redirect('quotations:create')
    client = get_object_or_404(Client, pk=client_id, company=company)

    if not quotation:
        quotation = Quotation(client=client, company=company)
    else:
        quotation.client = client

    raw_date = data.get('invoice_date', '').strip()
    quotation.quotation_date = datetime.date.fromisoformat(raw_date) if raw_date else datetime.date.today()
    quotation.gst_type = data.get('gst_type', 'cgst_sgst')
    quotation.buyer_order_no = data.get('buyer_order_no', '')
    po_date_str = data.get('buyer_order_date', '').strip()
    quotation.buyer_order_date = datetime.date.fromisoformat(po_date_str) if po_date_str else None
    quotation.dispatch_through = data.get('dispatch_through', '')
    quotation.terms_conditions = data.get('terms_conditions', '')
    quotation.notes = data.get('notes', '')
    due_date_str = data.get('due_date', '').strip()
    if due_date_str:
        quotation.due_date = datetime.date.fromisoformat(due_date_str)

    items_data = json.loads(data.get('items_json', '[]'))
    for item in items_data:
        product = None
        product_id = item.get('product_id')
        description = str(item.get('description', '')).strip()
        if product_id:
            product = Product.objects.filter(company=company, is_active=True, pk=product_id).first()
        elif description:
            product = Product.objects.filter(company=company, is_active=True, name__iexact=description).first()
        if product:
            item['product_id'] = product.id
            item['description'] = product.name
            if not str(item.get('hsn_sac', '')).strip():
                item['hsn_sac'] = product.hsn_sac
            if not str(item.get('unit', '')).strip():
                item['unit'] = product.unit
            if Decimal(str(item.get('rate', 0) or 0)) == 0:
                item['rate'] = str(product.rate)
            if int(item.get('gst_rate', 0) or 0) == 0:
                item['gst_rate'] = product.gst_rate

    subtotal = cgst = sgst = igst = Decimal('0')
    for item in items_data:
        qty = Decimal(str(item.get('quantity', 0)))
        rate = Decimal(str(item.get('rate', 0)))
        disc = Decimal(str(item.get('discount_pct', 0)))
        gst_rate = int(item.get('gst_rate', 0))
        amt = qty * rate * (1 - disc / 100)
        subtotal += amt
        gst_amt = amt * gst_rate / 100
        if quotation.gst_type == 'igst':
            igst += gst_amt
        elif quotation.gst_type == 'cgst_sgst':
            cgst += gst_amt / 2
            sgst += gst_amt / 2

    quotation.subtotal = subtotal
    quotation.taxable_amount = subtotal
    quotation.cgst_amount = cgst
    quotation.sgst_amount = sgst
    quotation.igst_amount = igst
    quotation.total_gst = cgst + sgst + igst
    quotation.grand_total = subtotal + quotation.total_gst
    quotation.balance_due = quotation.grand_total - quotation.amount_paid
    quotation.save()

    quotation.items.all().delete()
    for i, item in enumerate(items_data, 1):
        if not str(item.get('description', '')).strip():
            continue
        QuotationItem.objects.create(
            quotation=quotation, sl_no=i,
            product_id=item.get('product_id') or None,
            description=item.get('description', ''),
            hsn_sac=item.get('hsn_sac', ''),
            unit=item.get('unit', 'Nos'),
            quantity=Decimal(str(item.get('quantity', 1))),
            rate=Decimal(str(item.get('rate', 0))),
            discount_pct=Decimal(str(item.get('discount_pct', 0))),
            gst_rate=int(item.get('gst_rate', 0)),
            amount=Decimal(str(item.get('amount', 0))),
        )
    messages.success(request, f'Quotation {quotation.quotation_number} saved!')
    return redirect('quotations:detail', pk=quotation.pk)


@company_required
def quotation_detail(request, pk):
    company = get_company(request.user)
    quotation = get_object_or_404(Quotation, pk=pk, company=company)
    payments = quotation.payments.all()
    return render(request, 'quotations/detail.html', {
        'quotation': quotation,
        'invoice': quotation,
        'payments': payments,
        'payment_form': QuotationPaymentForm(),
        'today': datetime.date.today(),
        'cu': get_company_user(request.user),
    })


@company_required
def quotation_delete(request, pk):
    company = get_company(request.user)
    quotation = get_object_or_404(Quotation, pk=pk, company=company)
    cu = get_company_user(request.user)
    if cu and cu.role == 'staff':
        messages.error(request, 'Staff cannot cancel quotations.')
        return redirect('quotations:detail', pk=pk)
    if request.method == 'POST':
        quotation.status = 'cancelled'
        quotation.save()
        messages.success(request, 'Quotation cancelled.')
        return redirect('quotations:list')
    return render(request, 'quotations/confirm_delete.html', {'quotation': quotation})


@company_required
def quotation_print(request, pk):
    company = get_company(request.user)
    quotation = get_object_or_404(Quotation, pk=pk, company=company)
    return render(request, 'quotations/print.html', {'quotation': quotation, 'invoice': quotation, 'company': company})


@company_required
def add_payment(request, pk):
    company = get_company(request.user)
    cu = get_company_user(request.user)
    if cu and cu.role == 'staff':
        messages.error(request, 'Staff cannot record payments.')
        return redirect('quotations:detail', pk=pk)
    quotation = get_object_or_404(Quotation, pk=pk, company=company)
    if request.method == 'POST':
        form = QuotationPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.quotation = quotation
            payment.save()
            messages.success(request, f'Payment of Rs.{payment.amount} recorded!')
        else:
            messages.error(request, 'Payment form error.')
    return redirect('quotations:detail', pk=pk)


@company_required
def delete_payment(request, pk, payment_pk):
    company = get_company(request.user)
    cu = get_company_user(request.user)
    if cu and cu.role == 'staff':
        messages.error(request, 'Staff cannot delete payments.')
        return redirect('quotations:detail', pk=pk)
    payment = get_object_or_404(QuotationPayment, pk=payment_pk, quotation__company=company, quotation_id=pk)
    if request.method == 'POST':
        quotation = payment.quotation
        payment.delete()
        paid = quotation.payments.aggregate(t=Sum('amount'))['t'] or Decimal('0')
        quotation.amount_paid = paid
        quotation.balance_due = quotation.grand_total - paid
        quotation.status = 'paid' if quotation.balance_due <= 0 else ('partial' if paid > 0 else 'sent')
        quotation.save()
        messages.success(request, 'Payment deleted.')
    return redirect('quotations:detail', pk=pk)


@company_required
def send_whatsapp(request, pk):
    company = get_company(request.user)
    quotation = get_object_or_404(Quotation, pk=pk, company=company)
    phone = (quotation.client.whatsapp_number or '').replace('+', '').replace(' ', '').replace('-', '')
    if not phone:
        messages.error(request, 'No WhatsApp number for this client.')
        return redirect('quotations:detail', pk=pk)
    import urllib.parse
    msg = (f"Dear {quotation.client.vendor_name},\n\n"
           f"Please find Quotation {quotation.quotation_number} dated {quotation.quotation_date.strftime('%d-%b-%Y')}.\n"
           f"Amount: Rs.{quotation.grand_total:,.2f}\n"
           f"Due: {quotation.due_date.strftime('%d-%b-%Y') if quotation.due_date else 'N/A'}\n\n"
           f"Regards,\n{company.name}")
    return redirect(f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}")


@company_required
def mark_sent(request, pk):
    company = get_company(request.user)
    quotation = get_object_or_404(Quotation, pk=pk, company=company)
    if quotation.status == 'draft':
        Quotation.objects.filter(pk=quotation.pk).update(status='sent')
        messages.success(request, 'Quotation marked as Sent.')
    return redirect('quotations:detail', pk=pk)


@company_required
def calculate_totals(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        items = data.get('items', [])
        gst_type = data.get('gst_type', 'cgst_sgst')
        subtotal = cgst = sgst = igst = Decimal('0')
        for item in items:
            qty = Decimal(str(item.get('quantity', 0)))
            rate = Decimal(str(item.get('rate', 0)))
            disc = Decimal(str(item.get('discount_pct', 0)))
            gstr = int(item.get('gst_rate', 0))
            amt = qty * rate * (1 - disc / 100)
            subtotal += amt
            ga = amt * gstr / 100
            if gst_type == 'igst':
                igst += ga
            else:
                cgst += ga / 2
                sgst += ga / 2
        grand = subtotal + cgst + sgst + igst
        return JsonResponse({
            'subtotal': str(subtotal),
            'cgst': str(cgst),
            'sgst': str(sgst),
            'igst': str(igst),
            'total_gst': str(cgst + sgst + igst),
            'grand_total': str(grand),
        })
    return JsonResponse({'error': 'POST required'}, status=405)
