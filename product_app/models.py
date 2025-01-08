from django.db import models
# from authentication_app.model import Vendor
from django.contrib.auth.models import User



# Temporary Vendor model for testing
class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=225)
    vendor_phone = models.CharField(max_length=15)
    vendor_email = models.EmailField()
    vendor_address = models.TextField()
    store_name = models.CharField(max_length=225)
    store_address = models.TextField()

    def __str__(self):
        return self.vendor_name

class Category(models.Model):
    name = models.CharField(max_length=225)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=225)
    created_by = models.ForeignKey('Vendor', on_delete=models.CASCADE)
    category = models.ForeignKey('Category',on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.name}"
    
class Attribute(models.Model):
    name = models.CharField(max_length=225)
    created_by = models.ForeignKey('Vendor',on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.name}"
    
class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute,on_delete=models.CASCADE)
    value = models.CharField(max_length=225)
    created_by = models.ForeignKey('Vendor',on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.attribute.name}: {self.value}"
    
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sku = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='product_variant_images/', null=True, blank=True)
    price = models.IntegerField()
    stock = models.IntegerField()
    def __str__(self):
        return f"{self.product.name} - {self.sku}"
    
class ProductVariantAttribute(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.variant.sku} | {self.attribute.name}: {self.value.value}"
    
    
