from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from core.tenancy import get_company
from core.tenancy import SUPERADMIN_COMPANY_SESSION_KEY

def smart_home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.is_superuser and request.session.get(SUPERADMIN_COMPANY_SESSION_KEY):
        return redirect('dashboard:index')
    if request.user.is_superuser:
        return redirect('superadmin:company_list')
    return redirect('dashboard:index')

urlpatterns = [
    path('', smart_home),
    path('admin/', admin.site.urls),
    path('login/',  auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('superadmin/', include('superadmin.urls', namespace='superadmin')),
    path('dashboard/', include('dashboard.urls',   namespace='dashboard')),
    path('clients/',   include('clients.urls',     namespace='clients')),
    path('products/',  include('products.urls',    namespace='products')),
    path('invoices/',  include('invoices.urls',    namespace='invoices')),
    path('quotations/', include('quotations.urls', namespace='quotations')),
    path('returns/',    include('returns.urls',    namespace='returns')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
