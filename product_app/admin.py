from django.contrib import admin
from .models import Vendor, Product, Attribute, AttributeValue, ProductVariant, ProductVariantAttribute

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('vendor_name', 'vendor_phone', 'vendor_email', 'store_name')
    search_fields = ('vendor_name', 'store_name')
    list_filter = ('vendor_address',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by')
    search_fields = ('name',)
    list_filter = ('created_by',)

@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by')
    search_fields = ('name',)
    list_filter = ('created_by',)

@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('attribute', 'value', 'created_by')
    search_fields = ('value',)
    list_filter = ('attribute', 'created_by')

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'sku', 'image')
    search_fields = ('sku', 'product__name')
    list_filter = ('product',)

@admin.register(ProductVariantAttribute)
class ProductVariantAttributeAdmin(admin.ModelAdmin):
    list_display = ('variant', 'attribute', 'value')
    search_fields = ('variant__sku', 'attribute__name', 'value__value')
    list_filter = ('attribute', 'value')
