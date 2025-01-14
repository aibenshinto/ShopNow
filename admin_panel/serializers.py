from rest_framework import serializers
from authentication_app.models import Customer, Vendor


class VendorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_phone', 'vendor_email', 'vendor_address', 'store_name', 'store_address']

class CustomerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_name', 'customer_phone', 'customer_email', 'customer_address']
