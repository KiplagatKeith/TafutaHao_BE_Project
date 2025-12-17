# tenants/models.py
from django.db import models
from django.contrib.auth import get_user_model
from properties.models import Property
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()

class TenantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class FavoriteProperty(models.Model):
    tenant = models.ForeignKey(TenantProfile, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)

@receiver(post_save, sender=TenantProfile)
def assign_tenant_role(sender, instance, created, **kwargs):
    if created:
        instance.user.role = 'tenant'
        instance.user.save()