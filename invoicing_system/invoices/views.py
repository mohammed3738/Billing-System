from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.conf import settings
from .models import Invoice, InvoiceItem, Payment
from .forms import PaymentForm
from clients.models import Client
from products.models import Product
from core.tenancy import company_required, get_company, get_company_user
from decimal import Decimal
import json, datetime

@company_required
def invoice_list(request):
    company = get_company(request.user)
    status = request.GET.get('status', '')
    q      = request.GET.get('q', '')
    date_from = request.GET.get('date_from', '').strip()
    date_to   = request.GET.get('date_to', '').strip()
    today  = datetime.date.today()
    Invoice.objects.filter(company=company, due_date__lt=today,
        status__in=['sent','partial','draft']).update(status='overdue')
    invoices = Invoice.objects.filter(company=company).select_related('client')
    if status:
        invoices = invoices.filter(status=status)
    if q:
        invoices = invoices.filter(Q(invoice_number__icontains=q)|Q(client__vendor_name__icontains=q))
    if date_from:
        invoices = invoices.filter(invoice_date__gte=date_from)
    if date_to:
        invoices = invoices.filter(invoice_date__lte=date_to)
    return render(request, 'invoices/list.html', {
        'invoices': invoices, 'status': status, 'q': q,
        'date_from': date_from, 'date_to': date_to,
        'status_choices': Invoice._meta.get_field('status').choices,
    })

@company_required
def invoice_create(request):
    company = get_company(request.user)
    if request.method == 'POST':
        return _save_invoice(request, None, company)
    clients = Client.objects.filter(company=company, is_active=True)
    return render(request, 'invoices/form.html', {
        'title': 'New Invoice', 'clients': clients,
        'today': datetime.date.today().strftime('%Y-%m-%d'),
        'company_gst': company.gst_no or '',
    })

@company_required
def invoice_edit(request, pk):
    company = get_company(request.user)
    invoice = get_object_or_404(Invoice, pk=pk, company=company)
    cu = get_company_user(request.user)
    # Staff can only edit drafts
    if cu and cu.role == 'staff' and invoice.status not in ('draft',):
        messages.error(request, 'Staff can only edit draft invoices.')
        return redirect('invoices:detail', pk=pk)
    if request.method == 'POST':
        return _save_invoice(request, invoice, company)
    clients = Client.objects.filter(company=company, is_active=True)
    items = list(invoice.items.values())
    return render(request, 'invoices/form.html', {
        'title': f'Edit {invoice.invoice_number}', 'invoice': invoice,
        'clients': clients, 'items_json': json.dumps(items, default=str),
        'today': datetime.date.today().strftime('%Y-%m-%d'),
        'company_gst': company.gst_no or '',
    })

def _save_invoice(request, invoice, company):
    data = request.POST
    client_id = data.get('client_id')
    if not client_id:
        messages.error(request, 'Please select a client.')
        return redirect('invoices:create')
    client = get_object_or_404(Client, pk=client_id, company=company)

    if not invoice:
        invoice = Invoice(client=client, company=company)
    else:
        invoice.client = client

    invoice.invoice_date     = data.get('invoice_date') or datetime.date.today()
    invoice.gst_type         = data.get('gst_type', 'cgst_sgst')
    invoice.buyer_order_no   = data.get('buyer_order_no', '')
    po_date_str              = data.get('buyer_order_date', '').strip()
    invoice.buyer_order_date = po_date_str if po_date_str else None
    invoice.dispatch_through = data.get('dispatch_through', '')
    invoice.terms_conditions = data.get('terms_conditions', '')
    invoice.notes            = data.get('notes', '')
    due_date_str             = data.get('due_date', '').strip()
    if due_date_str:
        invoice.due_date = due_date_str

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
        qty      = Decimal(str(item.get('quantity', 0)))
        rate     = Decimal(str(item.get('rate', 0)))
        disc     = Decimal(str(item.get('discount_pct', 0)))
        gst_rate = int(item.get('gst_rate', 0))
        amt      = qty * rate * (1 - disc / 100)
        subtotal += amt
        gst_amt   = amt * gst_rate / 100
        if invoice.gst_type == 'igst':
            igst += gst_amt
        elif invoice.gst_type == 'cgst_sgst':
            cgst += gst_amt / 2
            sgst += gst_amt / 2

    invoice.subtotal      = subtotal
    invoice.taxable_amount= subtotal
    invoice.cgst_amount   = cgst
    invoice.sgst_amount   = sgst
    invoice.igst_amount   = igst
    invoice.total_gst     = cgst + sgst + igst
    invoice.grand_total   = subtotal + invoice.total_gst
    invoice.balance_due   = invoice.grand_total - invoice.amount_paid
    invoice.save()

    invoice.items.all().delete()
    for i, item in enumerate(items_data, 1):
        if not str(item.get('description', '')).strip():
            continue
        InvoiceItem.objects.create(
            invoice=invoice, sl_no=i,
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
    messages.success(request, f'Invoice {invoice.invoice_number} saved!')
    return redirect('invoices:detail', pk=invoice.pk)

@company_required
def invoice_detail(request, pk):
    company = get_company(request.user)
    invoice = get_object_or_404(Invoice, pk=pk, company=company)
    payments = invoice.payments.all()
    return render(request, 'invoices/detail.html', {
        'invoice': invoice, 'payments': payments,
        'payment_form': PaymentForm(),
        'today': datetime.date.today(),
        'cu': get_company_user(request.user),
    })

@company_required
def invoice_delete(request, pk):
    company = get_company(request.user)
    invoice = get_object_or_404(Invoice, pk=pk, company=company)
    cu = get_company_user(request.user)
    if cu and cu.role == 'staff':
        messages.error(request, 'Staff cannot cancel invoices.')
        return redirect('invoices:detail', pk=pk)
    if request.method == 'POST':
        invoice.status = 'cancelled'
        invoice.save()
        messages.success(request, 'Invoice cancelled.')
        return redirect('invoices:list')
    return render(request, 'invoices/confirm_delete.html', {'invoice': invoice})

@company_required
def invoice_print(request, pk):
    company = get_company(request.user)
    invoice = get_object_or_404(Invoice, pk=pk, company=company)
    return render(request, 'invoices/print.html', {'invoice': invoice, 'company': company})

@company_required
def add_payment(request, pk):
    company = get_company(request.user)
    cu      = get_company_user(request.user)
    if cu and cu.role == 'staff':
        messages.error(request, 'Staff cannot record payments.')
        return redirect('invoices:detail', pk=pk)
    invoice = get_object_or_404(Invoice, pk=pk, company=company)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            p.invoice = invoice
            p.save()
            messages.success(request, f'Payment of Rs.{p.amount} recorded!')
        else:
            messages.error(request, 'Payment form error.')
    return redirect('invoices:detail', pk=pk)

@company_required
def delete_payment(request, pk, payment_pk):
    company = get_company(request.user)
    cu      = get_company_user(request.user)
    if cu and cu.role == 'staff':
        messages.error(request, 'Staff cannot delete payments.')
        return redirect('invoices:detail', pk=pk)
    payment = get_object_or_404(Payment, pk=payment_pk, invoice__company=company, invoice_id=pk)
    if request.method == 'POST':
        inv = payment.invoice
        payment.delete()
        paid = inv.payments.aggregate(t=Sum('amount'))['t'] or Decimal('0')
        inv.amount_paid = paid
        inv.balance_due = inv.grand_total - paid
        inv.status = 'paid' if inv.balance_due <= 0 else ('partial' if paid > 0 else 'sent')
        inv.save()
        messages.success(request, 'Payment deleted.')
    return redirect('invoices:detail', pk=pk)

@company_required
def send_whatsapp(request, pk):
    company = get_company(request.user)
    invoice = get_object_or_404(Invoice, pk=pk, company=company)
    phone = (invoice.client.whatsapp_number or '').replace('+','').replace(' ','').replace('-','')
    if not phone:
        messages.error(request, 'No WhatsApp number for this client.')
        return redirect('invoices:detail', pk=pk)
    import urllib.parse
    msg = (f"Dear {invoice.client.vendor_name},\n\n"
           f"Please find Invoice {invoice.invoice_number} dated {invoice.invoice_date.strftime('%d-%b-%Y')}.\n"
           f"Amount: Rs.{invoice.grand_total:,.2f}\n"
           f"Due: {invoice.due_date.strftime('%d-%b-%Y') if invoice.due_date else 'N/A'}\n\n"
           f"Regards,\n{company.name}")
    return redirect(f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}")

@company_required
def mark_sent(request, pk):
    company = get_company(request.user)
    invoice = get_object_or_404(Invoice, pk=pk, company=company)
    if invoice.status == 'draft':
        invoice.status = 'sent'
        invoice.save()
        messages.success(request, 'Invoice marked as Sent.')
    return redirect('invoices:detail', pk=pk)

@company_required
def calculate_totals(request):
    if request.method == 'POST':
        data     = json.loads(request.body)
        items    = data.get('items', [])
        gst_type = data.get('gst_type', 'cgst_sgst')
        subtotal = cgst = sgst = igst = Decimal('0')
        for item in items:
            qty  = Decimal(str(item.get('quantity', 0)))
            rate = Decimal(str(item.get('rate', 0)))
            disc = Decimal(str(item.get('discount_pct', 0)))
            gstr = int(item.get('gst_rate', 0))
            amt  = qty * rate * (1 - disc / 100)
            subtotal += amt
            ga = amt * gstr / 100
            if gst_type == 'igst': igst += ga
            else: cgst += ga/2; sgst += ga/2
        grand = subtotal + cgst + sgst + igst
        return JsonResponse({'subtotal': str(subtotal), 'cgst': str(cgst),
            'sgst': str(sgst), 'igst': str(igst),
            'total_gst': str(cgst+sgst+igst), 'grand_total': str(grand)})
    return JsonResponse({'error': 'POST required'}, status=405)
