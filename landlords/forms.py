# landlords/forms.py

from django import forms
from properties.models import Property
from properties.constants import KENYA_COUNTIES
from django.contrib.auth.forms import PasswordChangeForm
from accounts.models import CustomUser

# Custom widget to allow multiple file uploads
class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

# Form for Property model
class PropertyForm(forms.ModelForm):
    county = forms.ChoiceField(
        choices=[('', 'Select County')] + [(c, c) for c in KENYA_COUNTIES],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        label="County"
    )

    
    class Meta:
        model = Property
        fields = [
            'house_type',
            'house_number',
            'rent',
            'county',
            'town',
            'location',
            'description',
            'available',
        ]

        labels = {
            'house_type': 'House Type',
        }

        widgets = {
            'house_type': forms.Select(attrs={'class': 'form-control'}),
            'house_number': forms.TextInput(attrs={'class': 'form-control'}),
            'rent': forms.NumberInput(attrs={'class': 'form-control'}),
            'town': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class LandlordAccountForm(forms.ModelForm):
    password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput,
        required=False,
        help_text="Leave blank if you don't want to change the password"
    )
    password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput,
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("Passwords do not match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user