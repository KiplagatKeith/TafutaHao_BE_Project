# landlords/views.py

from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from properties.models import Property, PropertyImage
from .models import LandlordProfile
from .forms import PropertyForm
from django.db.models import Q
from .mixins import LandlordRequiredMixin
from accounts.decorators import landlord_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST


# =========================
# List properties for landlord
# =========================
class LandlordPropertyListView(LoginRequiredMixin, LandlordRequiredMixin, ListView):
    model = Property
    template_name = 'landlords/property_list.html'
    context_object_name = 'properties'
    paginate_by = 6

    def get_queryset(self):
        user = self.request.user

        # Base queryset: ONLY this landlord's properties
        queryset = Property.objects.filter(landlord__user=user)

        # ---- GET FILTER VALUES ----
        q = self.request.GET.get('q', '').strip()
        min_rent = self.request.GET.get('min_rent')
        max_rent = self.request.GET.get('max_rent')
        county = self.request.GET.get('county', '').strip()
        town = self.request.GET.get('town', '').strip()
        location = self.request.GET.get('location', '').strip()
        house_type = self.request.GET.get('house_type', '').strip()

        # ---- APPLY FILTERS ----
        if q:
            queryset = queryset.filter(
                Q(description__icontains=q) |
                Q(house_number__icontains=q)
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

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ---- Persist filter values in template ----
        context.update({
            'search_query': self.request.GET.get('q', ''),
            'min_rent': self.request.GET.get('min_rent', ''),
            'max_rent': self.request.GET.get('max_rent', ''),
            'county': self.request.GET.get('county', ''),
            'town': self.request.GET.get('town', ''),
            'location': self.request.GET.get('location', ''),
            'house_type': self.request.GET.get('house_type', ''),
        })

        # ---- Populate dropdowns (same as tenant view) ----
        context['counties'] = (
            Property.objects
            .filter(landlord__user=self.request.user)
            .values_list('county', flat=True)
            .distinct()
        )

        context['towns'] = (
            Property.objects
            .filter(landlord__user=self.request.user)
            .values_list('town', flat=True)
            .distinct()
        )

        return context
    
# =========================
# Add new property
# =========================
class LandlordPropertyCreateView(LoginRequiredMixin, LandlordRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'
    success_url = reverse_lazy('landlords:landlord_dashboard')
    permission_required = 'properties.can_add_property'

    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (user.has_perm(self.permission_required) or user.is_landlord())

    # Pass extra data to template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Add Property"
        context['button_text'] = "Add Property"
        context['cancel_url'] = reverse_lazy('landlords:landlord_dashboard')
        return context

    # Save property and handle uploaded images
    def form_valid(self, form):
        # Link property to landlord
        landlord_profile, _ = LandlordProfile.objects.get_or_create(user=self.request.user)
        form.instance.landlord = landlord_profile  # assign landlord
        
        response = super().form_valid(form)

        # Handle multiple images
        files = self.request.FILES.getlist('images')
        for f in files:
            PropertyImage.objects.create(property=self.object, image=f)

        return response


# =========================
# Edit existing property
# =========================
class LandlordPropertyUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'
    success_url = reverse_lazy('landlords:landlord_dashboard')
    permission_required = 'properties.can_edit_property'

    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (user.has_perm(self.permission_required) or user.is_landlord())

    # Only allow editing properties owned by this landlord
    def get_queryset(self):
        return Property.objects.filter(landlord__user=self.request.user)

    # Add existing images to context for display in template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = PropertyImage.objects.filter(property=self.object)
        context['editing'] = True
        context['title'] = f"Edit Property: {self.object.get_house_type_display()} - {self.object.house_number}"
        context['button_text'] = "Save Changes"
        context['cancel_url'] = reverse_lazy('landlords:landlord_dashboard')
        return context

    # Save updated property and any new images
    def form_valid(self, form):
        response = super().form_valid(form)

        # Save new images uploaded during edit
        files = self.request.FILES.getlist('images')
        for f in files:
            PropertyImage.objects.create(property=self.object, image=f)

        return response


# =========================
# Delete property
# =========================
class LandlordPropertyDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Property
    permission_required = 'properties.can_delete_property'

    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (user.has_perm(self.permission_required) or user.is_landlord())

    def get_queryset(self):
        return Property.objects.filter(landlord__user=self.request.user)

    # Delete the property and respond with JSON if AJAX
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('landlords:landlord_dashboard')


# =========================
# Landlord dashboard
# =========================
@method_decorator(landlord_required, name='dispatch')
class LandlordDashboardView(LoginRequiredMixin, LandlordRequiredMixin, TemplateView):
    template_name = 'landlords/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        landlord_profile = getattr(self.request.user, 'landlordprofile', None)

        if landlord_profile:
            properties_list = landlord_profile.property_set.all()
            context['total_properties'] = properties_list.count()
            context['available_properties'] = properties_list.filter(available=True).count()

            # Paginate properties (6 per page)
            paginator = Paginator(properties_list, 6)
            page_number = self.request.GET.get('page')
            context['properties'] = paginator.get_page(page_number)
        else:
            context['total_properties'] = 0
            context['available_properties'] = 0
            context['properties'] = []

        return context


# =========================
# Delete individual property image (AJAX)
# =========================
@require_POST
def delete_property_image(request, image_id):
    image = get_object_or_404(PropertyImage, id=image_id, property__landlord__user=request.user)
    image.delete()
    return JsonResponse({'success': True})
