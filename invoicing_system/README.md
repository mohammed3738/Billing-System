# Invoicing System — Multi-Tenant Edition

## Architecture

```
Taxporium (Django superuser)
    └── Creates Companies: Zaco Computers, SH Computers, NAS Steels…
            └── Each Company has:
                    ├── Users (Admin / Staff roles)
                    ├── Clients (isolated per company)
                    ├── Products (isolated per company)
                    └── Invoices (isolated per company)
```

**Data Isolation**: Zaco Computers cannot see SH Computers' data. Each company's clients, products, and invoices are completely separate.

---

## Setup (3 commands)

Create a PostgreSQL database first, then provide the connection settings in a `.env` file:

```env
POSTGRES_DB=invoicing_system
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

```bash
pip install -r requirements.txt
python setup.py          # migrations + sample data + superuser prompt
python manage.py runserver
```

Open: **http://127.0.0.1:8000/**

---

## Login Guide

| Who | Login | Gets |
|-----|-------|------|
| **Taxporium** | Django superuser | Company Management panel |
| **Zaco Admin** | Company user (admin role) | Full dashboard, invoices, clients, products |
| **Zaco Staff** | Company user (staff role) | Invoice creation & viewing only |

---

## Features

### ✅ Multi-Tenant Companies
- Taxporium (superadmin) creates client companies
- Each company: Name, PAN, GSTIN, Address, Phone, Email, Website, Logo
- Bank details: Beneficiary name, account, IFSC, branch
- Invoice prefix per company (e.g. ZAC/26-27/1)

### ✅ User Roles per Company
- **Admin**: Full control (clients, products, invoices, payments)
- **Staff**: Invoice creation and viewing only

### ✅ Invoice Creation
- Live line-item table with product autocomplete (type → suggestions appear)
- Get-or-create: type a new product name → inline quick-create modal
- PO Date field added under Invoice Details
- Description is a free-text field in the invoice row (not from product master)
- Auto GST detection: compares first 2 digits of company GSTIN vs client GSTIN
  - Same state → CGST + SGST auto-selected
  - Different state → IGST auto-selected
  - User can still override manually

### ✅ GST Toggle
- CGST+SGST / IGST / Exempt — 3-button switcher
- Auto-detect badge shows when system picked the type

### ✅ Payment Tracking
- Record payments (Cash/Cheque/UPI/NEFT)
- Balance due tracker with progress bar
- Staff cannot record or delete payments

### ✅ WhatsApp Send
- Opens wa.me with pre-filled invoice message

### ✅ Print / PDF
- Clean A4 invoice with company logo, bank details, PO date

### ✅ Dashboard
- Sales KPIs, monthly chart, top clients, overdue alerts

---

## URL Guide

| URL | Who | What |
|-----|-----|------|
| `/` | All | Smart redirect based on role |
| `/login/` | All | Login page |
| `/superadmin/` | Taxporium only | Company management |
| `/dashboard/` | Company users | Sales dashboard |
| `/invoices/` | Company users | Invoices |
| `/clients/` | Company users | Clients |
| `/products/` | Admin only | Products |
| `/admin/` | Taxporium | Django admin |

---

## Product Master
- Fields: Name, HSN/SAC, Unit, Rate, GST Rate, Service flag
- Description removed (description is typed fresh in each invoice row)
- Category removed (simplified)

## Invoice Item Row
- Description: free-text (auto-filled from product but editable)
- HSN/SAC: auto-filled from product
- Rate, Unit, GST% all auto-filled but editable
