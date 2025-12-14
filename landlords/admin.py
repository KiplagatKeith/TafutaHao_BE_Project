# landlords/admin.py

from django.contrib import admin
from .models import LandlordProfile

class LandlordProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')  # <-- adjust this
    # if phone is on CustomUser:
    def phone_number(self, obj):
        return obj.user.phone_number
    phone_number.short_description = 'Phone'
