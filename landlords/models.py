# landlords/models.py

from django.db import models
from django.contrib.auth import get_user_model  # <- use your new user model
from django.db.models.signals import post_save
from django.dispatch import receiver
from properties.models import Property

User = get_user_model()

class LandlordProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='landlordprofile')
    # any other fields

@receiver(post_save, sender=LandlordProfile)
def assign_landlord_role(sender, instance, created, **kwargs):
    if created:
        instance.user.role = 'landlord'
        instance.user.save()

# ---------------- Landlord Favorite Properties ----------------

class LandlordFavoriteProperty(models.Model):
    landlord = models.ForeignKey(LandlordProfile, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('landlord', 'property')  # prevent duplicates

    def __str__(self):
        return f"{self.landlord.user.username} favorites {self.property.house_number}"