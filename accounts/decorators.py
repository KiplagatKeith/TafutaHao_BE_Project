# accounts/decorators.py

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

# Decorator to ensure the user is a landlord
def landlord_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_landlord():
            return redirect('no_permission')  # will create this page
        return view_func(request, *args, **kwargs)
    return wrapper
