# accounts/urls.py

from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import TenantSignupView, landlord_register, TenantLogoutView, RoleBasedLoginView

app_name = 'accounts'

urlpatterns = [
    path('login/', RoleBasedLoginView.as_view(), name='login'),
    path('logout/', TenantLogoutView.as_view(), name='logout'),

    path('signup/', TenantSignupView.as_view(), name='signup'),
   
    path('landlord-register/', landlord_register, name='landlord_register'),
]