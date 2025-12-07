# accounts/views.py

from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm
from .models import CustomUser
from django.contrib.auth.decorators import login_required
from landlords.models import LandlordProfile
from django.contrib.auth.views import LoginView, LogoutView
from tenants.models import TenantProfile
from django.contrib import messages


# Signs up a new user and creates the corresponding profile
class TenantSignupView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = "accounts/signup.html"

    def form_valid(self, form):
        # create user but don't commit yet
        user = form.save(commit=False)
        role = form.cleaned_data.get('role')      # role will be 'tenant' or 'landlord'
        user.role = role                         # set role properly
        user.save()                              # save user

        # create the corresponding profile immediately
        if role == 'tenant':
            TenantProfile.objects.get_or_create(user=user)
        elif role == 'landlord':
            LandlordProfile.objects.get_or_create(user=user)

        # log the user in so request.user reflects the new role
        login(self.request, user)

        messages.success(self.request, f'Account created as {role.capitalize()}! You are now logged in.')

        # redirect to the right namespaced view
        if role == 'tenant':
            return redirect('tenants:browse_properties')
        else:
            return redirect('landlords:landlord_dashboard')

@login_required
def landlord_register(request):
    if request.method == "POST":
        # Create LandlordProfile for the logged-in user
        LandlordProfile.objects.create(user=request.user)
        # Update the user's role
        request.user.role = 'landlord'
        request.user.save()
        # Redirect to landlord dashboard or property list
        return redirect('landlords:landlord_property_list')
    
    return render(request, 'accounts/landlord_register.html')

# Login and Logout views
class RoleBasedLoginView(LoginView):
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        """After successful login, redirect based on role."""
        user = form.get_user()
        login(self.request, user)

        # Redirect depending on profile
        if hasattr(user, 'landlordprofile'):
            return redirect('landlords:landlord_dashboard')
        else:
            return redirect('tenants:browse_properties')
        
class TenantLogoutView(LogoutView):
    next_page = 'tenants:browse_properties'  # where to redirect after logout

# --- PREVIOUS TINGS DELETED ---
"""
def choose_role(request):
    return render(request, "accounts/choose_role.html")

class TenantLoginView(LoginView):
    template_name = 'accounts/login.html'

"""