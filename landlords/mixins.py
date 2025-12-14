# landlords/mixins.py
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect

class LandlordRequiredMixin(UserPassesTestMixin):
    """
    Mixin to allow access only to users who have a LandlordProfile.
    """
    def test_func(self):
        #check if the user is authenticated and is a landlord
        return self.request.user.is_authenticated and self.request.user.is_landlord()

    def handle_no_permission(self):
        # Redirect non-landlords to tenant browsing page
        return redirect('tenants:browse_properties')
