from django.urls import path
from . import views

app_name = 'returns'

urlpatterns = [
    path('',              views.returns_list,  name='list'),
    path('add/',          views.return_create, name='create'),
    path('<int:pk>/edit/', views.return_edit,  name='edit'),
    path('<int:pk>/delete/', views.return_delete, name='delete'),
]
