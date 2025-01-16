from rest_framework import serializers
from .models import Order, OrderItem,ORDER_STATUS_CHOICES
from payment_app.models import RazorpayOrder

class RazorpayOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = RazorpayOrder
        fields = ['payment_id', 'payment_status', 'unique_order_id']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'quantity', 'price', 'unique_order_id']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    razorpay_details = RazorpayOrderSerializer(source='razorpay_order', read_only=True)


    class Meta:
        model = Order
        fields = ['id', 'order_id', 'user', 'total_price', 'status', 'created_at', 'updated_at', 'items','customer_email','vendor_email','razorpay_details']

class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    razorpay_order = RazorpayOrderSerializer(read_only=True)
    status_display = serializers.SerializerMethodField()
    created_at_formatted = serializers.SerializerMethodField()
    updated_at_formatted = serializers.SerializerMethodField()
    razorpay_details = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'order_id',
            'user',
            'total_price',
            'status',
            'status_display',
            'customer_email',
            'vendor_email',
            'created_at_formatted',
            'updated_at_formatted',
            'items',
            'razorpay_order',
            'razorpay_details'
        ]

    def get_status_display(self, obj):
        return dict(ORDER_STATUS_CHOICES)[obj.status]

    def get_created_at_formatted(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")

    def get_updated_at_formatted(self, obj):
        return obj.updated_at.strftime("%Y-%m-%d %H:%M:%S")