from django.db import models
from authentication_app.models import Customer  # Import the Customer model
from product_app.models import Product, ProductVariant  # Importing from product_app

class Cart(models.Model):
    """
    Model to represent shopping carts for both authenticated customers and guest users.
    """
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, null=True, blank=True)  # For authenticated customers
    session_id = models.CharField(max_length=255, null=True, blank=True)  # For guest users
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_checked = models.BooleanField(default=False)

    

    def __str__(self):
        if self.customer:
            return f"Cart for {self.customer.customer_name}"
        return f"Cart for session: {self.session_id}"
    
    def calculate_total(self):
        total = 0
        # Iterate over each item in the cart and sum the total
        for item in self.items.all():
            total += item.get_price() * item.quantity
        return total
    
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
    


