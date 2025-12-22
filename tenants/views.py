# tenants/views.py

from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView, FormView, DeleteView, UpdateView
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from properties.models import Property
from .models import TenantProfile, FavoriteProperty
from accounts.models import CustomUser
from django.urls import reverse_lazy
from django.db.models import Q
from .models import FavoriteProperty
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.forms import CustomUserCreationForm
from django.views.generic.edit import CreateView
from properties.constants import KENYA_COUNTIES
from django.contrib.auth import get_user_model


User = get_user_model()
# -------------------------
# Browse Properties with Pagination and Search/Filter
# -------------------------
class BrowsePropertiesView(ListView):
    model = Property
    template_name = 'tenants/browse_properties.html'
    context_object_name = 'properties'
    paginate_by = 6

    def get_queryset(self):
        queryset = Property.objects.filter(available=True)

        q = self.request.GET.get('q', '')
        min_rent = self.request.GET.get('min_rent')
        max_rent = self.request.GET.get('max_rent')
        county = self.request.GET.get('county', '').strip().title()
        town = self.request.GET.get('town', '').strip().title()
        location = self.request.GET.get('location', '')
        house_type = self.request.GET.get('house_type', '')

        if q:
            queryset = queryset.filter(
                Q(description__icontains=q) |
                Q(location__icontains=q) |
                Q(house_type__icontains=q)
            )

        if min_rent:
            queryset = queryset.filter(rent__gte=min_rent)
        if max_rent:
            queryset = queryset.filter(rent__lte=max_rent)
        if county:
            queryset = queryset.filter(county__iexact=county)
        if town:
            queryset = queryset.filter(town__iexact=town)
        if location:
            queryset = queryset.filter(location__icontains=location)
        if house_type:
            queryset = queryset.filter(house_type=house_type)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['counties'] = KENYA_COUNTIES
        context['county'] = self.request.GET.get('county', '').strip().title()
        context['town'] = self.request.GET.get('town', '').strip().title()

        # Populate town dropdown dynamically
        if context['county']:
            towns = Property.objects.filter(county__iexact=context['county']).values_list('town', flat=True).distinct()
        else:
            towns = Property.objects.values_list('town', flat=True).distinct()
        context['towns'] = sorted([t.strip().title() for t in towns])

        # Keep other filter values
        context['search_query'] = self.request.GET.get('q', '')
        context['min_rent'] = self.request.GET.get('min_rent', '')
        context['max_rent'] = self.request.GET.get('max_rent', '')
        context['location'] = self.request.GET.get('location', '')
        context['house_type'] = self.request.GET.get('house_type', '')

         # Favorite properties
        user = self.request.user
        if user.is_authenticated:
            tenant_profile = getattr(user, 'tenantprofile', None)
            if tenant_profile:
                context['favorite_property_ids'] = tenant_profile.favoriteproperty_set.values_list('property_id', flat=True)
            else:
                context['favorite_property_ids'] = []
        else:
            context['favorite_property_ids'] = []

        return context
# -------------------------
# Favorite / Unfavorite Property
# -------------------------
class FavoritePropertyView(View):
    def post(self, request, property_id):
        if not request.user.is_authenticated:
            messages.error(request, "You need to login to favorite properties.")
            return redirect('login')

        tenant_profile, _ = TenantProfile.objects.get_or_create(user=request.user)
        property_obj = get_object_or_404(Property, id=property_id)

        favorite = FavoriteProperty.objects.filter(tenant=tenant_profile, property=property_obj).first()
        if favorite:
            favorite.delete()
            messages.info(request, "Property removed from favorites.")
        else:
            FavoriteProperty.objects.create(tenant=tenant_profile, property=property_obj)
            messages.success(request, "Property added to favorites.")

        return redirect('tenants:browse_properties')

class FavoritePropertyDeleteView(LoginRequiredMixin, DeleteView):
    model = FavoriteProperty
    template_name = 'shared/confirm_delete.html'  # shared template
    success_url = reverse_lazy('tenants:tenant_profile')  # back to tenant profile page

    def get_queryset(self):
        # Only allow deleting favorites of the logged-in tenant
        tenant_profile = getattr(self.request.user, 'tenantprofile', None)
        return FavoriteProperty.objects.filter(tenant=tenant_profile)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass dynamic object name & cancel URL for template
        context['object_name'] = f"{self.object.property.get_house_type_display()} - {self.object.property.house_number}"
        context['cancel_url'] = reverse_lazy('tenants:tenant_profile')
        return context
    
# -------------------------
# Tenant Profile
# -------------------------
class TenantProfileView(View):
    template_name = 'tenants/profile.html'

    def get(self, request):
        if not request.user.is_authenticated:
            messages.error(request, "You need to login to view your profile.")
            return redirect('login')

        tenant_profile, _ = TenantProfile.objects.get_or_create(user=request.user)
        favorite_properties = tenant_profile.favoriteproperty_set.select_related('property').all()

        context = {
            'tenant_profile': tenant_profile,
            'favorite_properties': favorite_properties,
        }
        return render(request, self.template_name, context)

class RequestViewingView(LoginRequiredMixin, View):
    def get(self, request, property_id):
        property_obj = get_object_or_404(Property, id=property_id)

        # You can implement your "request viewing" logic here,
        # e.g., send email to landlord or create a Request model
        messages.success(request, f"You have requested a viewing for {property_obj.get_house_type_display} - {property_obj.house_number}")

        return redirect('properties:property_detail', pk=property_id)

# Update Tenant Account
class TenantAccountUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'tenants/tenant_account_edit.html'
    fields = ['username', 'email', 'phone_number']

    def get_object(self):
        # Tenant can ONLY edit their own user account
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Your account has been updated successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('tenants:tenant_profile')
    
# Delete Tenant Acc
class TenantProfileDeleteView(LoginRequiredMixin, DeleteView):
    model = TenantProfile
    template_name = 'shared/confirm_delete.html'
    success_url = reverse_lazy('tenants:browse_properties')

    def get_object(self):
        return TenantProfile.objects.get(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_name'] = 'your tenant profile'
        context['cancel_url'] = reverse_lazy('tenants:tenant_account_edit')
        return context

    def delete(self, request, *args, **kwargs):
        # Get TenantProfile and related User
        tenant_profile = self.get_object()
        user = tenant_profile.user

        # Log out BEFORE deleting
        logout(request)

        # Delete User (this cascades to TenantProfile if using OneToOne)
        user.delete()

        # Redirect to a safe page
        return super(DeleteView, self).delete(request, *args, **kwargs)