from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
import uuid
from payment_app.models import RazorpayOrder


ORDER_STATUS_CHOICES = [
    ('Processing', 'Processing'),
    ('Shipped', 'Shipped'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled'),
]


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    order_id = models.CharField(max_length=50, unique=True, editable=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='Processing')
    customer_email = models.EmailField(null=True, blank=True, default='farizzkp123@gmail.com')  # Default customer email
    vendor_email = models.EmailField(null=True, blank=True, default='farizz1132pulikkal@gmail.com')  # Default vendor email
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    razorpay_order = models.OneToOneField(
        RazorpayOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order",
        help_text="Link to the Razorpay order for this order"
    )

    def __str__(self):
        return f"Order {self.order_id} - {self.user if self.user else 'Anonymous'}"



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unique_order_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.product_name} (x{self.quantity})"
