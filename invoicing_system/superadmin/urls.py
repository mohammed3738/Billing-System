from django.urls import path
from . import views

app_name = 'superadmin'

urlpatterns = [
    path('',                                    views.company_list,       name='company_list'),
    path('enter-company/<int:pk>/',             views.enter_company,      name='enter_company'),
    path('exit-company/',                       views.exit_company,       name='exit_company'),
    path('company/create/',                     views.company_create,     name='company_create'),
    path('company/<int:pk>/',                   views.company_detail,     name='company_detail'),
    path('company/<int:pk>/edit/',              views.company_edit,       name='company_edit'),
    path('company/<int:pk>/delete/',            views.company_delete,     name='company_delete'),
    path('company/<int:pk>/add-user/',          views.add_company_user,   name='add_user'),
    path('company/<int:pk>/user/<int:user_pk>/remove/', views.remove_company_user, name='remove_user'),
    path('company/<int:pk>/user/<int:user_pk>/role/',   views.change_user_role,    name='change_role'),
    path('my-company/users/',                   views.tenant_user_list,   name='tenant_users'),
    path('my-company/users/add/',               views.tenant_add_user,    name='tenant_add_user'),
    path('my-company/users/<int:user_pk>/remove/', views.tenant_remove_user, name='tenant_remove_user'),
    path('my-company/users/<int:user_pk>/role/', views.tenant_change_user_role, name='tenant_change_role'),
]
