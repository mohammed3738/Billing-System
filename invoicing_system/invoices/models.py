from django.db import models
from django.utils import timezone
from clients.models import Client
from products.models import Product
import datetime

INVOICE_STATUS = [
    ('draft',    'Draft'),
    ('sent',     'Sent'),
    ('partial',  'Partially Paid'),
    ('paid',     'Paid'),
    ('overdue',  'Overdue'),
    ('cancelled','Cancelled'),
]
GST_TYPE_CHOICES = [
    ('cgst_sgst', 'CGST + SGST (Intra-State)'),
    ('igst',      'IGST (Inter-State)'),
    ('exempt',    'GST Exempt'),
]
PAYMENT_MODE = [
    ('cash','Cash'),('cheque','Cheque'),('neft','NEFT/RTGS'),
    ('upi','UPI'),('bank_transfer','Bank Transfer'),('other','Other'),
]

class Invoice(models.Model):
    company          = models.ForeignKey(
        'superadmin.Company', on_delete=models.CASCADE,
        related_name='invoices', null=True, blank=True
    )
    invoice_number   = models.CharField(max_length=50, blank=True)
    invoice_sequence = models.IntegerField(default=1)
    client           = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='invoices')
    invoice_date     = models.DateField(default=datetime.date.today)
    due_date         = models.DateField(null=True, blank=True)

    # PO Details
    buyer_order_no   = models.CharField(max_length=100, blank=True)
    buyer_order_date = models.DateField(null=True, blank=True)   # ← new
    dispatch_through = models.CharField(max_length=100, blank=True)
    destination      = models.CharField(max_length=100, blank=True)

    gst_type         = models.CharField(max_length=20, choices=GST_TYPE_CHOICES, default='cgst_sgst')

    subtotal         = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discount_amount  = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    taxable_amount   = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    cgst_amount      = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    sgst_amount      = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    igst_amount      = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_gst        = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    grand_total      = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    amount_paid      = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    balance_due      = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    terms_conditions = models.TextField(blank=True, default=(
        "1. No Warranty by physical Damage & Burnt Goods.\n"
        "2. If Cheque is Dishonoured Rs. 500/- will be charged.\n"
        "3. Any complain regarding goods received must be made within 24 hrs.\n"
        "4. Received Above Goods in good condition."
    ))
    notes  = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=INVOICE_STATUS, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-invoice_date', '-invoice_sequence']
        # invoice_number unique per company
        unique_together = [['company', 'invoice_number']]

    def __str__(self):
        return self.invoice_number or str(self.pk)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last = Invoice.objects.filter(company=self.company).order_by('-invoice_sequence').first()
            seq  = (last.invoice_sequence + 1) if last else 1
            self.invoice_sequence = seq
            if self.company:
                prefix = self.company.invoice_prefix or 'INV'
                fy     = self.company.financial_year or '26-27'
            else:
                from django.conf import settings
                prefix = getattr(settings, 'INVOICE_PREFIX', 'INV')
                fy     = getattr(settings, 'FINANCIAL_YEAR', '26-27')
            self.invoice_number = f"{prefix}/{fy}/{seq}"
        if self.due_date is None and self.invoice_date:
            days = self.client.term_in_days if self.client_id else 30
            inv_d = self.invoice_date
            if isinstance(inv_d, str):
                inv_d = datetime.date.fromisoformat(inv_d)
            self.due_date = inv_d + datetime.timedelta(days=days)
        self.balance_due = self.grand_total - self.amount_paid
        if self.balance_due <= 0 and self.grand_total > 0:
            self.status = 'paid'
        elif self.amount_paid > 0:
            self.status = 'partial'
        super().save(*args, **kwargs)

    def get_status_color(self):
        return {'draft':'secondary','sent':'info','partial':'warning',
                'paid':'success','overdue':'danger','cancelled':'dark'}.get(self.status,'secondary')


class InvoiceItem(models.Model):
    invoice      = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    sl_no        = models.IntegerField(default=1)
    product      = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    description  = models.CharField(max_length=500)
    hsn_sac      = models.CharField(max_length=20, blank=True)
    unit         = models.CharField(max_length=20, default='Nos')
    quantity     = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    rate         = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_pct = models.DecimalField(max_digits=5,  decimal_places=2, default=0)
    amount       = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    gst_rate     = models.IntegerField(default=0)

    class Meta:
        ordering = ['sl_no']

    def save(self, *args, **kwargs):
        disc = self.rate * self.quantity * self.discount_pct / 100
        self.amount = (self.rate * self.quantity) - disc
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice} - {self.description[:30]}"


class Payment(models.Model):
    invoice      = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateField(default=datetime.date.today)
    amount       = models.DecimalField(max_digits=14, decimal_places=2)
    mode         = models.CharField(max_length=20, choices=PAYMENT_MODE, default='cash')
    reference_no = models.CharField(max_length=100, blank=True)
    notes        = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.invoice} - Rs.{self.amount} on {self.payment_date}"

    def save(self, *args, **kwargs):
        from decimal import Decimal
        super().save(*args, **kwargs)
        inv = self.invoice
        inv.amount_paid = sum(p.amount for p in inv.payments.all())
        inv.balance_due = inv.grand_total - inv.amount_paid
        inv.status = 'paid' if inv.balance_due <= 0 else ('partial' if inv.amount_paid > 0 else inv.status)
        Invoice.objects.filter(pk=inv.pk).update(
            amount_paid=inv.amount_paid, balance_due=inv.balance_due, status=inv.status)
