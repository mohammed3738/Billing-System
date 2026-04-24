from django.urls import path
from . import views

app_name = 'quotations'

urlpatterns = [
    path('', views.quotation_list, name='list'),
    path('create/', views.quotation_create, name='create'),
    path('<int:pk>/', views.quotation_detail, name='detail'),
    path('<int:pk>/edit/', views.quotation_edit, name='edit'),
    path('<int:pk>/delete/', views.quotation_delete, name='delete'),
    path('<int:pk>/print/', views.quotation_print, name='print'),
    path('<int:pk>/mark-sent/', views.mark_sent, name='mark_sent'),
    path('<int:pk>/whatsapp/', views.send_whatsapp, name='whatsapp'),
    # path('<int:pk>/payment/add/', views.add_payment, name='add_payment'),
    # path('<int:pk>/payment/<int:payment_pk>/delete/', views.delete_payment, name='delete_payment'),
    path('api/calculate/', views.calculate_totals, name='calculate'),
]
