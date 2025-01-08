from rest_framework import serializers
from .models import Product, Variant, Cart, CartItem

class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model.
    """
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'is_active', 'created_at', 'updated_at']


class VariantSerializer(serializers.ModelSerializer):
    """
    Serializer for the Variant model.
    """
    product = ProductSerializer()  # Nested serializer to include product details

    class Meta:
        model = Variant
        fields = ['id', 'product', 'name', 'price', 'stock', 'created_at', 'updated_at']


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for CartItem model.
    """
    product = ProductSerializer()
    variant = VariantSerializer()

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
