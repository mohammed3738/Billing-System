from django.db import models
from clients.models import Client
from products.models import Product
import datetime

# QUOTATION_STATUS = [
#     ('draft', 'Draft'),
#     ('sent', 'Sent'),
#     ('partial', 'Partially Paid'),
#     ('paid', 'Paid'),
#     ('overdue', 'Overdue'),
#     ('cancelled', 'Cancelled'),
# ]
GST_TYPE_CHOICES = [
    ('cgst_sgst', 'CGST + SGST (Intra-State)'),
    ('igst', 'IGST (Inter-State)'),
    ('exempt', 'GST Exempt'),
]
# PAYMENT_MODE = [
#     ('cash', 'Cash'), ('cheque', 'Cheque'), ('neft', 'NEFT/RTGS'),
#     ('upi', 'UPI'), ('bank_transfer', 'Bank Transfer'), ('other', 'Other'),
# ]


class Quotation(models.Model):
    company = models.ForeignKey(
        'superadmin.Company', on_delete=models.CASCADE,
        related_name='quotations', null=True, blank=True
    )
    quotation_number = models.CharField(max_length=50, blank=True)
    quotation_sequence = models.IntegerField(default=1)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='quotations')
    quotation_date = models.DateField(default=datetime.date.today)
    due_date = models.DateField(null=True, blank=True)

    buyer_order_no = models.CharField(max_length=100, blank=True)
    buyer_order_date = models.DateField(null=True, blank=True)
    dispatch_through = models.CharField(max_length=100, blank=True)
    destination = models.CharField(max_length=100, blank=True)

    gst_type = models.CharField(max_length=20, choices=GST_TYPE_CHOICES, default='cgst_sgst')

    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    taxable_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    cgst_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    sgst_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    igst_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_gst = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    balance_due = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    terms_conditions = models.TextField(blank=True, default=(
        "1. No Warranty by physical Damage & Burnt Goods.\n"
        "2. If Cheque is Dishonoured Rs. 500/- will be charged.\n"
        "3. Any complain regarding goods received must be made within 24 hrs.\n"
        "4. Received Above Goods in good condition."
    ))
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-quotation_date', '-quotation_sequence']
        unique_together = [['company', 'quotation_number']]

    def __str__(self):
        return self.quotation_number or str(self.pk)

    # def save(self, *args, **kwargs):
        if not self.quotation_number:
            last = Quotation.objects.filter(company=self.company).order_by('-quotation_sequence').first()
            seq = (last.quotation_sequence + 1) if last else 1
            self.quotation_sequence = seq
            if self.company:
                prefix = (self.company.invoice_prefix or 'INV').replace('INV', 'QTN')
                fy = self.company.financial_year or '26-27'
            else:
                prefix = 'QTN'
                fy = '26-27'
            self.quotation_number = f"{prefix}/{fy}/{seq}"
        if self.due_date is None and self.quotation_date:
            days = self.client.term_in_days if self.client_id else 30
            qd = self.quotation_date
            if isinstance(qd, str):
                qd = datetime.date.fromisoformat(qd)
            self.due_date = qd + datetime.timedelta(days=days)
        self.balance_due = self.grand_total - self.amount_paid
        if self.balance_due <= 0 and self.grand_total > 0:
            self.status = 'paid'
        elif self.amount_paid > 0:
            self.status = 'partial'
        super().save(*args, **kwargs)


class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='items')
    sl_no = models.IntegerField(default=1)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=500)
    hsn_sac = models.CharField(max_length=20, blank=True)
    unit = models.CharField(max_length=20, default='Nos')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    gst_rate = models.IntegerField(default=0)

    class Meta:
        ordering = ['sl_no']

    def save(self, *args, **kwargs):
        disc = self.rate * self.quantity * self.discount_pct / 100
        self.amount = (self.rate * self.quantity) - disc
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quotation} - {self.description[:30]}"


# class QuotationPayment(models.Model):
#     quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='payments')
#     payment_date = models.DateField(default=datetime.date.today)
#     amount = models.DecimalField(max_digits=14, decimal_places=2)
#     mode = models.CharField(max_length=20, choices=PAYMENT_MODE, default='cash')
#     reference_no = models.CharField(max_length=100, blank=True)
#     notes = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['-payment_date']

#     def __str__(self):
#         return f"{self.quotation} - Rs.{self.amount} on {self.payment_date}"

#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
#         quotation = self.quotation
#         quotation.amount_paid = sum(p.amount for p in quotation.payments.all())
#         quotation.balance_due = quotation.grand_total - quotation.amount_paid
#         quotation.status = 'paid' if quotation.balance_due <= 0 else ('partial' if quotation.amount_paid > 0 else quotation.status)
#         Quotation.objects.filter(pk=quotation.pk).update(
#             amount_paid=quotation.amount_paid,
#             balance_due=quotation.balance_due,
#             status=quotation.status,
#         )
