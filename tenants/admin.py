# tenants/admin.py

from django.contrib import admin
from .models import TenantProfile, FavoriteProperty
from django.db import models

@admin.register(TenantProfile)
class TenantProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)

@admin.register(FavoriteProperty)
class FavoritePropertyAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'property', 'saved_at')
    search_fields = ('tenant__user__username', 'property__house_number')
    saved_at = models.DateTimeField(auto_now_add=True)