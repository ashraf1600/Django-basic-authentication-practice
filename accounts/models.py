from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    You can add extra fields here as needed.
    """
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.username