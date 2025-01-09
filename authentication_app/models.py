from django.contrib.auth.models import User
from django.db import models

class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile')
    vendor_name = models.CharField(max_length=100)
    vendor_phone = models.CharField(max_length=15)
    vendor_email = models.EmailField(unique=True)
    vendor_address = models.TextField()
    store_name = models.CharField(max_length=100)
    store_address = models.TextField()

    def __str__(self):
        return self.store_name


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=15)
    customer_email = models.EmailField(unique=True)
    customer_address = models.TextField()

    def __str__(self):
        return self.customer_name
