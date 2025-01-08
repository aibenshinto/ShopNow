from django.contrib import admin
from .models import Vendor, Category, Product, Attribute, AttributeValue, ProductVariant, ProductVariantAttribute

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('vendor_name', 'vendor_phone', 'vendor_email', 'store_name')  # Fields to display in the list view
    search_fields = ('vendor_name', 'vendor_email', 'store_name')  # Add search functionality
    list_filter = ('store_name',)  # Add filters

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_by', 'category')  # Display key fields
    search_fields = ('name', 'created_by__vendor_name', 'category__name')  # Search by related fields
    list_filter = ('category',)  # Filter by category

@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_by')
    search_fields = ('name',)
    list_filter = ('created_by',)

@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('id', 'attribute', 'value', 'created_by')
    search_fields = ('value',)
    list_filter = ('attribute',)

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'sku', 'price')
    search_fields = ('sku',)
    list_filter = ('product',)

@admin.register(ProductVariantAttribute)
class ProductVariantAttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'variant', 'attribute', 'value')  # Display price and related fields
    search_fields = ('variant__sku', 'attribute__name', 'value__value')  # Allow searching by variant or attribute
    list_filter = ('attribute', 'variant')  # Add filters for attributes and variants
