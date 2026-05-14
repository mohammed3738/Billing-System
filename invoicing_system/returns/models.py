from django.db import models
import os

RETURN_TYPE_CHOICES = [
    # GST Returns
    ('GSTR-1',  'GSTR-1 (Outward Supplies)'),
    ('GSTR-3B', 'GSTR-3B (Monthly Summary)'),
    ('GSTR-2B', 'GSTR-2B (Auto ITC Statement)'),
    ('GSTR-9',  'GSTR-9 (Annual Return)'),
    ('GSTR-9C', 'GSTR-9C (Reconciliation Statement)'),
    ('GSTR-4',  'GSTR-4 (Composition Scheme)'),
    # TDS / TCS
    ('TDS Payment', 'TDS Payment (Challan 281)'),
    ('TDS 24Q',     'TDS Return 24Q (Salary)'),
    ('TDS 26Q',     'TDS Return 26Q (Non-Salary)'),
    ('TDS 27Q',     'TDS Return 27Q (NRI Payments)'),
    ('TCS 27EQ',    'TCS Return 27EQ'),
    # Income Tax
    ('Advance Tax', 'Advance Tax'),
    ('ITR',         'Income Tax Return (ITR)'),
    # Other Compliance
    ('AIR/SFT',     'AIR / SFT (Fin. Transactions)'),
    ('PT Return',   'Professional Tax Return'),
    ('PF Return',   'PF Return (ECR)'),
    ('ESIC Return', 'ESIC Return'),
    ('ROC MGT-7',   'ROC Annual Return (MGT-7)'),
    ('ROC AOC-4',   'ROC Financial Statements (AOC-4)'),
    ('LUT Filing',  'LUT Filing (GST Export)'),
    ('Other',       'Other'),
]

FREQUENCY_CHOICES = [
    ('Monthly',     'Monthly'),
    ('Quarterly',   'Quarterly'),
    ('Half-Yearly', 'Half-Yearly'),
    ('Annual',      'Annual'),
    ('One-time',    'One-time'),
]

STATUS_CHOICES = [
    ('Pending',    'Pending'),
    ('Filed',      'Filed'),
    ('Late Filed', 'Late Filed'),
]

MONTH_CHOICES = [
    (1, 'January'),  (2, 'February'), (3, 'March'),    (4, 'April'),
    (5, 'May'),      (6, 'June'),     (7, 'July'),      (8, 'August'),
    (9, 'September'),(10, 'October'), (11, 'November'), (12, 'December'),
]


class TaxReturn(models.Model):
    company = models.ForeignKey(
        'superadmin.Company', on_delete=models.CASCADE, related_name='tax_returns'
    )
    return_type   = models.CharField(max_length=50, choices=RETURN_TYPE_CHOICES)
    frequency     = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='Monthly')
    month         = models.IntegerField(choices=MONTH_CHOICES, null=True, blank=True)
    year          = models.IntegerField()
    from_date     = models.DateField(null=True, blank=True)
    to_date       = models.DateField(null=True, blank=True)
    return_period = models.CharField(max_length=100, blank=True)
    due_date      = models.DateField(null=True, blank=True)
    filed_date    = models.DateField(null=True, blank=True)
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    computation_file  = models.FileField(upload_to='returns/computation/', blank=True, null=True)
    return_filed_file = models.FileField(upload_to='returns/filed/', blank=True, null=True)
    notes         = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['return_type', '-year', '-month']

    def __str__(self):
        return f"{self.return_type} — {self.return_period or self.year}"

    def get_month_name(self):
        return dict(MONTH_CHOICES).get(self.month, '') if self.month else ''

    @property
    def computation_filename(self):
        return os.path.basename(self.computation_file.name) if self.computation_file else None

    @property
    def filed_filename(self):
        return os.path.basename(self.return_filed_file.name) if self.return_filed_file else None
