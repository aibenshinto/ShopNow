from django.contrib import admin
from .models import Product, Variant, Cart, CartItem


class VariantInline(admin.TabularInline):
    """
    Inline for the Variant model to allow editing variants directly within the Product admin.
    """
    model = Variant
    extra = 1  # Number of empty forms to show initially


class CartItemInline(admin.TabularInline):
    """
    Inline for the CartItem model to allow editing cart items directly within the Cart admin.
    """
    model = CartItem
    extra = 1  # Number of empty forms to show initially


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin view for the Product model.
    """
    list_display = ('name', 'price', 'stock', 'is_active', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_active',)
    inlines = [VariantInline]  # Show variants inside the product admin


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    """
    Admin view for the Variant model.
    """
    list_display = ('product', 'name', 'price', 'stock', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('product',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Admin view for the Cart model.
    """
    list_display = ('user', 'session_id', 'created_at', 'updated_at')
    search_fields = ('user__username', 'session_id')
    list_filter = ('user', 'session_id')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """
    Admin view for the CartItem model.
    """
    list_display = ('cart', 'product', 'variant', 'quantity', 'created_at', 'updated_at')
    search_fields = ('cart__session_id', 'cart__user__username', 'product__name', 'variant__name')
    list_filter = ('cart', 'product', 'variant')
