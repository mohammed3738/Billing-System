from django.db import models

GST_RATE_CHOICES = [
    (0, '0%'),(5, '5%'),(12, '12%'),(18, '18%'),(28, '28%'),
]
UNIT_CHOICES = [
    ('Nos','Nos'),('Mtr','Mtr'),('Kg','Kg'),('Ltr','Ltr'),
    ('Pcs','Pcs'),('Box','Box'),('Set','Set'),('Roll','Roll'),
    ('Pair','Pair'),('Job','Job'),
]

class Product(models.Model):
    company  = models.ForeignKey(
        'superadmin.Company', on_delete=models.CASCADE,
        related_name='products', null=True, blank=True
    )
    name     = models.CharField(max_length=300)
    hsn_sac  = models.CharField(max_length=20, blank=True, verbose_name='HSN/SAC Code')
    unit     = models.CharField(max_length=20, choices=UNIT_CHOICES, default='Nos')
    rate     = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gst_rate = models.IntegerField(choices=GST_RATE_CHOICES, default=18)
    is_service = models.BooleanField(default=False)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
