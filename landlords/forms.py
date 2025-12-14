# landlords/forms.py

from django import forms
from properties.models import Property
from properties.constants import KENYA_COUNTIES


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

