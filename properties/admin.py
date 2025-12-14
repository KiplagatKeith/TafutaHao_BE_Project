# Django admin configuration for Property model

from django.contrib import admin
from .models import Property

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('house_type', 'house_number', 'landlord', 'rent', 'location', 'available')
    list_filter = ('house_type', 'available', 'location')  # Filters in sidebar
    search_fields = ('house_number', 'landlord__user__username', 'location')
