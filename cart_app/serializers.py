from rest_framework import serializers
from product_app.models import Product, ProductVariant
from .models import Cart, CartItem


class ProductVariantSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProductVariant model.
    """
    class Meta:
        model = ProductVariant
        fields = ['id', 'sku', 'name', 'price', 'stock']


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for CartItem model.
    """
    product = serializers.StringRelatedField()  # Display product name
    variant = ProductVariantSerializer()  # Nested serializer for variant

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'variant', 'quantity', 'created_at']


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for the Cart model.
    """
    items = CartItemSerializer(many=True, source='items.all')  # Use related name for CartItem

    class Meta:
        model = Cart
        fields = ['id', 'customer', 'created_at', 'items']
