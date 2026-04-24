from django.shortcuts import render, redirect
from django.db.models import Sum, Count
from invoices.models import Invoice
from clients.models import Client
from products.models import Product
from core.tenancy import company_required, get_company
import datetime, json

@company_required
def index(request):
    company = get_company(request.user)
    today = datetime.date.today()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - datetime.timedelta(days=1)).replace(day=1)
    last_month_end   = this_month_start - datetime.timedelta(days=1)

    Invoice.objects.filter(company=company, due_date__lt=today,
        status__in=['sent','partial','draft']).update(status='overdue')

    base = Invoice.objects.filter(company=company).exclude(status='cancelled')
    total_sales       = base.aggregate(t=Sum('grand_total'))['t'] or 0
    total_received    = base.aggregate(t=Sum('amount_paid'))['t'] or 0
    total_outstanding = base.aggregate(t=Sum('balance_due'))['t'] or 0
    overdue_qs        = Invoice.objects.filter(company=company, status='overdue')
    overdue_count     = overdue_qs.count()
    overdue_amount    = overdue_qs.aggregate(t=Sum('balance_due'))['t'] or 0

    this_month_sales = base.filter(invoice_date__gte=this_month_start).aggregate(t=Sum('grand_total'))['t'] or 0
    last_month_sales = base.filter(invoice_date__gte=last_month_start,
        invoice_date__lte=last_month_end).aggregate(t=Sum('grand_total'))['t'] or 0

    status_data = base.values('status').annotate(count=Count('id'), total=Sum('grand_total'))

    monthly_labels, monthly_totals = [], []
    for i in range(5, -1, -1):
        d = (today.replace(day=1) - datetime.timedelta(days=i*28)).replace(day=1)
        nd = (d + datetime.timedelta(days=32)).replace(day=1)
        amt = base.filter(invoice_date__gte=d, invoice_date__lt=nd).aggregate(t=Sum('grand_total'))['t'] or 0
        monthly_labels.append(d.strftime('%b %Y'))
        monthly_totals.append(float(amt))

    recent_invoices = Invoice.objects.filter(company=company).select_related('client').order_by('-invoice_date','-id')[:8]
    top_clients = base.values('client__vendor_name','client__client_code').annotate(total=Sum('grand_total')).order_by('-total')[:5]

    return render(request, 'dashboard/index.html', {
        'total_sales': total_sales, 'total_received': total_received,
        'total_outstanding': total_outstanding, 'overdue_count': overdue_count,
        'overdue_amount': overdue_amount, 'this_month_sales': this_month_sales,
        'last_month_sales': last_month_sales, 'status_data': list(status_data),
        'recent_invoices': recent_invoices, 'top_clients': top_clients,
        'total_clients': Client.objects.filter(company=company, is_active=True).count(),
        'total_products': Product.objects.filter(company=company, is_active=True).count(),
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_totals': json.dumps(monthly_totals),
        'today': today, 'company': company,
    })
