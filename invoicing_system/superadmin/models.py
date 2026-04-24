from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    """
    A tenant company (e.g. Zaco Computers, SH Computers).
    Created by Taxporium (superadmin). Each company has isolated data.
    """
    name            = models.CharField(max_length=200)
    pan             = models.CharField(max_length=20, blank=True)
    gst_no          = models.CharField(max_length=20, blank=True, verbose_name='GSTIN')
    address         = models.TextField(blank=True)
    telephone       = models.CharField(max_length=30, blank=True)
    mobile          = models.CharField(max_length=20, blank=True)
    email           = models.EmailField(blank=True)
    website         = models.URLField(blank=True)
    logo            = models.ImageField(upload_to='company_logos/', blank=True, null=True)

    # Bank details
    beneficiary_name    = models.CharField(max_length=200, blank=True)
    beneficiary_account = models.CharField(max_length=30, blank=True)
    beneficiary_ifsc    = models.CharField(max_length=20, blank=True)
    beneficiary_branch  = models.CharField(max_length=200, blank=True)

    # Invoice series prefix, e.g. "ZAC" → ZAC/26-27/1
    invoice_prefix  = models.CharField(max_length=10, default='INV')
    financial_year  = models.CharField(max_length=10, default='26-27')

    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Companies'
        ordering = ['name']

    def __str__(self):
        return self.name


COMPANY_ROLE = [
    ('admin', 'Admin (Full Control)'),
    ('staff', 'Staff (Invoice Creation & Viewing)'),
]

class CompanyUser(models.Model):
    """Links a Django User to a Company with a role."""
    user    = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_user')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='users')
    role    = models.CharField(max_length=20, choices=COMPANY_ROLE, default='staff')

    def __str__(self):
        return f"{self.user.username} → {self.company.name} ({self.role})"

    @property
    def is_admin(self):
        return self.role == 'admin'
