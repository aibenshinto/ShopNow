from django.contrib import admin

from .models import Customer, Vendor

# Register your models here.

admin.site.register(Vendor)
admin.site.register(Customer)