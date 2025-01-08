from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    """
    Model to represent products in the e-commerce app.
    """
    name = models.CharField(max_length=255)  # Product name
    description = models.TextField(blank=True, null=True)  # Optional product description
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Product price
    stock = models.PositiveIntegerField(default=0)  # Available stock
    created_at = models.DateTimeField(auto_now_add=True)  # Auto timestamp for creation
    updated_at = models.DateTimeField(auto_now=True)  # Auto timestamp for updates
    is_active = models.BooleanField(default=True)  # Whether the product is active or hidden

    def __str__(self):
        return self.name


class Variant(models.Model):
    """
    Model to represent product variants (e.g., size, color).
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    name = models.CharField(max_length=255)  # Variant name, e.g., "Red, XL"
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Override price if needed
    stock = models.PositiveIntegerField(default=0)  # Stock for the specific variant
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.name}"


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
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.variant:
            return f"{self.product.name} ({self.variant.name}) - Qty: {self.quantity}"
        return f"{self.product.name} - Qty: {self.quantity}"
