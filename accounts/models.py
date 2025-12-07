# accounts/models.py

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        """
        Create and save a regular user with the given username, email, and password.
        """
        if not username:
            raise ValueError("The Username field is required")

        # Normalize the email if provided
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """
        Create and save a superuser.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('tenant', 'Tenant'),
        ('landlord', 'Landlord'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='tenant')
    phone_number = models.CharField(max_length=15, blank=True)

    objects = CustomUserManager()  # attach the custom manager

    def is_landlord(self):
        return self.role == 'landlord'

    def is_tenant(self):
        return self.role == 'tenant'
