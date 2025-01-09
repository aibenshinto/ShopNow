from django.contrib import admin
from .models import  Product, Attribute, AttributeValue, ProductVariant, ProductVariantAttribute


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
