from django.db import models
from product_app.models import ProductVariant
from authentication_app.models import Customer
from authentication_app.models import Vendor
# Create your models here.


class Review(models.Model):
    product_variant = models.ForeignKey(ProductVariant,on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])  # 1 to 5 rating
    review_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.customer.customer_name}-{self.product_variant.sku}-{self.rating}"
    
class Reply(models.Model):
    review = models.ForeignKey(Review,on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor,on_delete=models.CASCADE)
    reply_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Reply to {self.review} by {self.vendor.vendor_name}"
    

    
    
    