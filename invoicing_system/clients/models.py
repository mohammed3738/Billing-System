from django.db import models
import os

DOCUMENT_TYPE_CHOICES = [
    ('PAN', 'PAN Card'),
    ('TAN', 'TAN Card'),
    ('PF', 'PF Registration'),
    ('Aadhaar', 'Aadhaar Card'),
    ('MSME', 'MSME / Udyam Registration'),
    ('ESIC', 'ESIC Registration'),
    ('GST', 'GST Certificate'),
    ('ITR', 'Income Tax Return'),
    ('Trade License', 'Trade License'),
    ('Shops & Establishment', 'Shops & Establishment'),
    ('Professional Tax', 'Professional Tax'),
    ('IEC', 'Import Export Code (IEC)'),
    ('Bank Statement', 'Bank Statement'),
    ('Other', 'Other'),
]

STATE_CHOICES = [
    ('Andhra Pradesh','Andhra Pradesh'),('Arunachal Pradesh','Arunachal Pradesh'),
    ('Assam','Assam'),('Bihar','Bihar'),('Chhattisgarh','Chhattisgarh'),
    ('Goa','Goa'),('Gujarat','Gujarat'),('Haryana','Haryana'),
    ('Himachal Pradesh','Himachal Pradesh'),('Jharkhand','Jharkhand'),
    ('Karnataka','Karnataka'),('Kerala','Kerala'),('Madhya Pradesh','Madhya Pradesh'),
    ('Maharashtra','Maharashtra'),('Manipur','Manipur'),('Meghalaya','Meghalaya'),
    ('Mizoram','Mizoram'),('Nagaland','Nagaland'),('Odisha','Odisha'),
    ('Punjab','Punjab'),('Rajasthan','Rajasthan'),('Sikkim','Sikkim'),
    ('Tamil Nadu','Tamil Nadu'),('Telangana','Telangana'),('Tripura','Tripura'),
    ('Uttar Pradesh','Uttar Pradesh'),('Uttarakhand','Uttarakhand'),
    ('West Bengal','West Bengal'),('Delhi','Delhi'),
]

PAYMENT_TERMS = [
    ('Immediate', 'Immediate'),
    ('7 days', '7 days'),
    ('15 days', '15 days'),
    ('30 days', '30 days'),
    ('45 days', '45 days'),
    ('60 days', '60 days'),
    ('90 days', '90 days'),
]

class Client(models.Model):
    company = models.ForeignKey(
        'superadmin.Company', on_delete=models.CASCADE,
        related_name='clients', null=True, blank=True
    )
    client_code   = models.CharField(max_length=10, blank=True)
    vendor_name   = models.CharField(max_length=200)
    gst_no        = models.CharField(max_length=20, blank=True, null=True)
    payment_terms = models.CharField(max_length=20, choices=PAYMENT_TERMS, default='30 days')
    term_in_days  = models.IntegerField(default=30)

    billing_address1       = models.CharField(max_length=200, blank=True)
    billing_address2       = models.CharField(max_length=200, blank=True)
    billing_city           = models.CharField(max_length=100, blank=True)
    billing_pin            = models.CharField(max_length=10,  blank=True)
    billing_state          = models.CharField(max_length=50,  choices=STATE_CHOICES, default='Maharashtra')
    billing_country        = models.CharField(max_length=50,  default='India')
    billing_email          = models.EmailField(blank=True)
    billing_contact_person = models.CharField(max_length=100, blank=True)
    billing_contact_no     = models.CharField(max_length=20,  blank=True)

    shipping_name           = models.CharField(max_length=200, blank=True)
    shipping_address1       = models.CharField(max_length=200, blank=True)
    shipping_address2       = models.CharField(max_length=200, blank=True)
    shipping_city           = models.CharField(max_length=100, blank=True)
    shipping_pin            = models.CharField(max_length=10,  blank=True)
    shipping_state          = models.CharField(max_length=50,  choices=STATE_CHOICES, default='Maharashtra')
    shipping_country        = models.CharField(max_length=50,  default='India')
    shipping_contact_person = models.CharField(max_length=100, blank=True)
    shipping_contact_no     = models.CharField(max_length=20,  blank=True)

    whatsapp_number = models.CharField(max_length=20,  blank=True)
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['client_code']

    def __str__(self):
        return f"{self.client_code} - {self.vendor_name}"


class ClientDocument(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    login_id = models.CharField(max_length=200, blank=True)
    password = models.CharField(max_length=200, blank=True)
    attachment = models.FileField(upload_to='client_documents/', blank=True, null=True)
    notes = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client} — {self.document_type}"

    @property
    def filename(self):
        if self.attachment:
            return os.path.basename(self.attachment.name)
        return None

    def save(self, *args, **kwargs):
        if not self.client_code:
            last = Client.objects.filter(company=self.company).order_by('-id').first()
            try:
                num = int(last.client_code[1:]) + 1 if (last and last.client_code) else 1
            except Exception:
                num = 1
            self.client_code = f"C{num:04d}"
        super().save(*args, **kwargs)
