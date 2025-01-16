from django.contrib import admin
from .models import AddressBook

@admin.register(AddressBook)
class AddressBookAdmin(admin.ModelAdmin):
    list_display = ("user", "address_line1", "city", "is_default", "created_at")
    search_fields = ("user__username", "address_line1", "city")
