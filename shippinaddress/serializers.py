from rest_framework import serializers
from .models import AddressBook

class AddressBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressBook
        fields = "__all__"

class AddressBookCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressBook
        exclude = ("user",)
