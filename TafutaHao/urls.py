"""
URL configuration for rental_system_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect, render
from django.conf import settings
from django.conf.urls.static import static

def home_redirect(request):
    return redirect('tenants:browse_properties')

def no_permission_view(request):
    return render(request, 'no_permission.html')

urlpatterns = [
    path('', home_redirect, name='home'),

    path('admin/', admin.site.urls),

    # Tenant property browsing & favorites
    path('browse/', include(('tenants.urls', 'tenants'), namespace = 'tenants')),

    # Tenant & Landlord Authentication (accounts app)
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),

    # Landlord dashboard & management
    path('landlord/', include(('landlords.urls', 'landlords'), namespace = 'landlords')),

    # Public property details
    path('properties/', include(('properties.urls', 'properties'), namespace = 'properties')),

    # No permission fallback
    path('no-permission/', no_permission_view, name='no_permission'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

