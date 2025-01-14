from django.db import models
from authentication_app.models import Vendor

class Category(models.Model):
    vendor = models.ForeignKey(Vendor, related_name='categories', on_delete=models.CASCADE)
    category = models.CharField(max_length=255)
    

    def __str__(self):
        return self.category