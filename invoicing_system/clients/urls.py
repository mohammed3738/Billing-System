from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    path('', views.client_list, name='list'),
    path('create/', views.client_create, name='create'),
    path('<int:pk>/', views.client_detail, name='detail'),
    path('<int:pk>/edit/', views.client_edit, name='edit'),
    path('<int:pk>/delete/', views.client_delete, name='delete'),
    path('api/get-or-create/', views.client_get_or_create, name='get_or_create'),
    path('api/search/', views.client_search_ajax, name='search_ajax'),
    path('api/<int:pk>/', views.client_detail_ajax, name='detail_ajax'),
    path('document/<int:pk>/delete/', views.document_delete, name='document_delete'),
]
