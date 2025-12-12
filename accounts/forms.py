# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model

User = get_user_model()

"""
UserChangeForm is Django’s built-in form for editing existing users, while
UserCreationForm is for creating new users.
"""

class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('', '--- Choose Role ---'),  # placeholder
        ('tenant', 'Tenant'),
        ('landlord', 'Landlord'),
    ]

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        label='Select Role',
        widget=forms.Select(attrs={'class': 'form-control'}),
        error_messages={'required': 'Please select a role to continue.'}
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'phone_number']
