from django.db import models
from django.contrib.auth.models import AbstractUser # change
# Create your models here.

class CustomUser(AbstractUser):
    ROLES=[
        ('admin','Admin'),
        ('customer','Customer'),
    ]

    user_role = models.CharField(max_length=50,choices=ROLES)
   

   