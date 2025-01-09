from rest_framework import serializers
from product_app.models import Product, ProductVariant  # Import from the product_app
from .models import Cart, CartItem

class ProductVariantSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProductVariant model.
    """
    class Meta:
        model = ProductVariant
        fields = ['id', 'product', 'sku', 'name', 'price', 'stock', 'created_at', 'updated_at']


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for CartItem model.
    """
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())  # Reference Product by ID
    variant = serializers.PrimaryKeyRelatedField(queryset=ProductVariant.objects.all(), required=False)  # Reference Variant by ID

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'variant', 'quantity', 'created_at', 'updated_at']


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for the Cart model.
    """
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'session_id', 'created_at', 'updated_at', 'items']
