# properties/views.py

from django.views.generic import ListView, DetailView
from .models import Property
from django.db.models import Q, F, Func, Value
from django.http import JsonResponse
from .constants import KENYA_COUNTIES
class PropertyListView(ListView):
    model = Property
    template_name = 'properties/property_list.html'
    context_object_name = 'properties'
    paginate_by = 10  # optional pagination

    def get_queryset(self):
        queryset = Property.objects.filter(available=True)  # Only show available properties

        # Get filter parameters from GET request
        q = self.request.GET.get('q', '')
        min_rent = self.request.GET.get('min_rent')
        max_rent = self.request.GET.get('max_rent')
        county = self.request.GET.get('county', '')
        town = self.request.GET.get('town', '')
        location = self.request.GET.get('location', '')        
        house_type = self.request.GET.get('house_type', '')

        # Apply text search filter
        if q:
            queryset = queryset.filter(
                Q(description__icontains=q) | Q(location__icontains=q) 
            )

        # Apply house type filter
        if house_type:
            queryset = queryset.filter(house_type=house_type)

        # Apply location filter
        if location:
            queryset = queryset.filter(location__icontains=location)

        # Filter by town
        if town:
            queryset = queryset.filter(town__icontains=town.strip())

        # Filter by county
        if county:
            queryset = queryset.filter(county__icontains=county.strip())

        # Apply rent range filter
        if min_rent:
            try:
                queryset = queryset.filter(rent__gte=int(min_rent))
            except ValueError:
                pass  # Ignore invalid input
        if max_rent:
            try:
                queryset = queryset.filter(rent__lte=int(max_rent))
            except ValueError:
                pass  # Ignore invalid input

        

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the current filter values back to template
        context['search_query'] = self.request.GET.get('q', '')

        context['house_type'] = self.request.GET.get('house_type', '')

        context['min_rent'] = self.request.GET.get('min_rent', '')
        context['max_rent'] = self.request.GET.get('max_rent', '')
        
        context['location'] = self.request.GET.get('location', '')
        context['county'] = self.request.GET.get('county', '').strip().title()
        context['town'] = self.request.GET.get('town', '').strip().title()
        
        # County dropdown: always all 47 counties A-Z
        context['counties'] = KENYA_COUNTIES

        # Town dropdown: dynamic based on selected county
        if context['county']:
            towns = Property.objects.filter(county__iexact=context['county']) \
                                    .values_list('town', flat=True).distinct()
        else:
            towns = Property.objects.values_list('town', flat=True).distinct()

        context['towns'] = sorted([t.strip().title() for t in towns])  # alphabetical
        return context

class PropertyDetailView(DetailView):
    model = Property
    template_name = 'properties/property_detail.html'
    context_object_name = 'property'

def get_towns_by_county(request):
    county = request.GET.get('county', '').strip()
    print("Requested county:", county)  # Debug

    if county:
        # Use case-insensitive filter and remove extra spaces
        towns = Property.objects.filter(county__iexact=county).values_list('town', flat=True).distinct()
        # Clean up town names too
        towns_list = sorted([t.strip().title() for t in towns])  # Normalize towns
    else:
        towns_list = []
        
    print("AJAX towns returned:", towns_list)  # Debug
    return JsonResponse({'towns': towns_list})
