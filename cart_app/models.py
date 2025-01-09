from django.db import models
from django.contrib.auth.models import User
from product_app.models import Product, ProductVariant  # Importing from product_app

class Cart(models.Model):
    """
    Model to represent shopping carts for both authenticated users and guest users.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # For logged-in users
    session_id = models.CharField(max_length=255, null=True, blank=True)  # For guest users
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Cart for session: {self.session_id}"

class CartItem(models.Model):
    """
    Model to represent items in the cart.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Reference to Product model in product_app
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)  # Reference to ProductVariant model in product_app
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.variant:
            return f"{self.product.name} ({self.variant.sku}) - Qty: {self.quantity}"  # Accessing variant SKU from product_app's ProductVariant model
        return f"{self.product.name} - Qty: {self.quantity}"

    def get_price(self):
        """Returns the price for the cart item."""
        if self.variant:
            return self.variant.price  # Get the price from ProductVariant
        return self.product.price  # Get the price from Product (in case there is no variant)

    def is_in_stock(self):
        """Check if there's enough stock for the cart item."""
        if self.variant:
            return self.variant.stock >= self.quantity  # Check variant stock
        return self.product.stock >= self.quantity  # Check product stock

class ShippingAddress(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE, related_name="shipping_address")
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.address_line_1}, {self.city}, {self.state}, {self.country}"