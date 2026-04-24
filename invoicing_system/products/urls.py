from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='list'),
    path('create/', views.product_create, name='create'),
    path('<int:pk>/edit/', views.product_edit, name='edit'),
    path('<int:pk>/delete/', views.product_delete, name='delete'),
    path('api/search/', views.product_search_ajax, name='search_ajax'),
    path('api/get-or-create/', views.product_get_or_create, name='get_or_create'),
]
