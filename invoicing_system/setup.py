#!/usr/bin/env python3
"""TFS Invoicing System - One-time setup script."""
import os, sys, subprocess

def run(cmd, **kw):
    print(f"  → {cmd}")
    r = subprocess.run(cmd, shell=True, **kw)
    if r.returncode != 0:
        print(f"  ✗ FAILED: {cmd}"); sys.exit(1)

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    print("\n╔══════════════════════════════╗")
    print("║  Invoicing System — Setup    ║")
    print("╚══════════════════════════════╝\n")

    print("1. Migrations...")
    run("python manage.py makemigrations superadmin clients products invoices")
    run("python manage.py migrate")

    print("\n2. Sample data...")
    run("""python manage.py shell -c "
from superadmin.models import Company, CompanyUser
from django.contrib.auth.models import User
from products.models import Product
from clients.models import Client

# Create sample company
co, _ = Company.objects.get_or_create(name='Zaco Computers', defaults={
    'gst_no': '27ABCDE1234F1Z5', 'address': 'Shop 5, MG Road, Thane, Maharashtra 400601',
    'mobile': '9876543210', 'email': 'info@zacocomputers.com',
    'invoice_prefix': 'ZAC', 'financial_year': '26-27',
    'beneficiary_name': 'Zaco Computers', 'beneficiary_account': '12345678901234',
    'beneficiary_ifsc': 'HDFC0001234', 'beneficiary_branch': 'Thane Main Branch',
})

# Sample products for Zaco
for p in [
    ('CP Plus 2MP HD IR Bullet Camera', '85258090', 'Nos', 1500, 18),
    ('5x5 Surface Box', '39269090', 'Nos', 100, 18),
    ('Wire BNC & DC Pin with Connection', '85444290', 'Nos', 100, 18),
    ('New Camera Installation Charge', '998719', 'Job', 500, 18),
    ('DVR & SMPS Wiring Alignment', '998719', 'Job', 2000, 18),
    ('Polycab 4+1 CCTV Cable', '85444290', 'Mtr', 40, 18),
    ('CCTV Wiring Labour Charges', '998719', 'Mtr', 45, 18),
]:
    Product.objects.get_or_create(company=co, name=p[0], defaults={'hsn_sac':p[1],'unit':p[2],'rate':p[3],'gst_rate':p[4],'is_service':p[2]=='Job'})

Client.objects.get_or_create(company=co, vendor_name='ANOOP C.H.S. LTD', defaults={
    'billing_address1':'Mira Road (E)','billing_city':'Thane',
    'billing_state':'Maharashtra','billing_pin':'401107',
})
print('Sample data loaded for Zaco Computers!')
"
""")

    print("\n3. Create Taxporium superadmin...")
    run("python manage.py createsuperuser")
    print("\n╔══════════════════════════════╗")
    print("║  Done! Run:                  ║")
    print("║  python manage.py runserver  ║")
    print("║  Open: http://127.0.0.1:8000 ║")
    print("╚══════════════════════════════╝\n")
    print("LOGIN GUIDE:")
    print("  Superadmin (Taxporium) → logs in → sees Company Management panel")
    print("  Company user (Zaco)    → logs in → sees Invoice/Client/Product panel\n")

if __name__ == '__main__':
    main()
