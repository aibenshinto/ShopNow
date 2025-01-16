from django.db import models
from cart_app.models import Cart  # Import the Cart model from cart_app

class RazorpayOrder(models.Model):
    """
    Model to represent an order created with Razorpay for a Cart.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)  # Link to the Cart
    order_id = models.CharField(max_length=255)  # Razorpay Order ID
    payment_id = models.CharField(max_length=255, blank=True, null=True)  # Razorpay Payment ID
    payment_status = models.CharField(
        max_length=50, 
        default="created",  # Default status is "created", can be updated to "paid"
        choices=[('created', 'Created'), ('paid', 'Paid'), ('failed', 'Failed')]
    )  # Payment status for the order (created, paid, or failed)
    unique_order_id = models.CharField(max_length=255, unique=True,null=True)
    def __str__(self):
        return f"Razorpay Order: {self.order_id} for Cart #{self.cart.id}"
    
