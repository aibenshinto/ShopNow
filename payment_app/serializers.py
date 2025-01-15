from rest_framework import serializers
from cart_app.models import Cart, CartItem  # Import the Cart and CartItem models from cart_app
from payment_app.models import RazorpayOrder  # Import RazorpayOrder from payment_app

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['product', 'quantity', 'price']  # Adjusted fields to match your CartItem model

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'customer', 'session_id', 'created_at', 'updated_at', 'items']  # Adjusted fields

class RazorpayOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = RazorpayOrder
        fields = ['order_id', 'payment_id', 'payment_status', 'cart']  # Fields to include for RazorpayOrder

class TransactionHistorySerializer(serializers.ModelSerializer):
    # Serialize RazorpayOrder related fields
    order_id = serializers.CharField(source='razorpayorder.order_id')
    payment_id = serializers.CharField(source='razorpayorder.payment_id')
    payment_status = serializers.CharField(source='razorpayorder.payment_status')

    class Meta:
        model = Cart
        fields = ['id', 'order_id', 'payment_id', 'payment_status', 'created_at']  # Added 'created_at' for more details
