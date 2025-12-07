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
    paginate_by = 6  # 6 properties per page

    # Check if user is landlord or has permission
    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (user.has_perm(self.permission_required) or user.is_landlord())

    # Filter properties based on search and filters
    def get_queryset(self):
        queryset = Property.objects.filter(landlord__user=self.request.user)
        query = self.request.GET.get('q', '')
        house_type = self.request.GET.get('house_type', '')
        available = self.request.GET.get('available', '')

        if query:
            queryset = queryset.filter(
                Q(house_number__icontains=query) |
                Q(location__icontains=query)
            )
        if house_type:
            queryset = queryset.filter(house_type=house_type)
        if available.lower() == 'true':
            queryset = queryset.filter(available=True)
        elif available.lower() == 'false':
            queryset = queryset.filter(available=False)
        return queryset

    # Pass filter values back to template for keeping them in forms
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['house_type'] = self.request.GET.get('house_type', '')
        context['available'] = self.request.GET.get('available', '')
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
        context['cancel_url'] = reverse_lazy('landlords:landlord_property_list')
        return context

    # Save property and handle uploaded images
    def form_valid(self, form):
        landlord_profile, _ = LandlordProfile.objects.get_or_create(user=self.request.user)
        form.instance.landlord = landlord_profile  # assign landlord
        response = super().form_valid(form)

        # Save each uploaded image to PropertyImage
        for img in self.request.FILES.getlist('images'):
            PropertyImage.objects.create(property=self.object, image=img)

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
        context['cancel_url'] = reverse_lazy('landlords:landlord_property_list')
        return context

    # Save updated property and any new images
    def form_valid(self, form):
        response = super().form_valid(form)
        for img in self.request.FILES.getlist('images'):
            PropertyImage.objects.create(property=self.object, image=img)
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
