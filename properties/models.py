# properties/models.py

from django.db import models

class Property(models.Model):
    HOUSE_TYPE = [
        ('single', 'Single Room'),
        ('bedsitter', 'Bedsitter'),
        ('1BR', 'One Bedroom'),
        ('2BR', 'Two Bedroom'),
        ('3BR', 'Three Bedroom'),
        ('shared', 'Shared Unit'),
    ]

    landlord = models.ForeignKey('landlords.LandlordProfile', on_delete=models.CASCADE)
    house_type = models.CharField(max_length=50, choices = HOUSE_TYPE)  # Bedsitter, 1BR, 2BR, etc.
    house_number = models.CharField(max_length=20)
    rent = models.IntegerField()

    county = models.CharField(max_length=255)
    town = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    description = models.TextField(blank=True)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.county = self.county.strip().title()  # e.g., " nairobi " → "Nairobi"
        self.town = self.town.strip().title()
        super().save(*args, **kwargs)
    class Meta:
        permissions = [
            ("can_add_property", "Can add property"),
            ("can_edit_property", "Can edit any property"),
            ("can_delete_property", "Can delete property"),
        ]
        
    def __str__(self):
        return f"{self.house_type} - {self.house_number}"

# New model for images
class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_photos/')
    
    def __str__(self):
        return f"Image for {self.property.house_number}"