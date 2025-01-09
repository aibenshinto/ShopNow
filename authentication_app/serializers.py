from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Vendor, Customer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class VendorSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Vendor
        fields = [ 'user','vendor_name', 'vendor_phone', 'vendor_email', 'vendor_address', 'store_name', 'store_address']


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Customer
        fields = ['user', 'customer_name', 'customer_phone', 'customer_email', 'customer_address']
