# from django.contrib import admin
# from .models import Cart, CartItem
# from product_app.models import Product, ProductVariant

# from .models import ShippingAddress

# # Optional: Define a custom admin class to customize the display
# class ShippingAddressAdmin(admin.ModelAdmin):
#     list_display = ('cart', 'address_line_1', 'city', 'state', 'postal_code', 'country')  # Fields to display in the list view
#     search_fields = ('cart__user__username', 'address_line_1', 'city', 'state', 'postal_code', 'country')  # Fields to enable search

# # Register the ShippingAddress model with the custom admin class
# admin.site.register(ShippingAddress, ShippingAddressAdmin)

# # Registering the Product model from product_app to show up in CartItem
# class CartItemInline(admin.TabularInline):
#     """
#     Inline model for CartItem within the Cart admin view.
#     """
#     model = CartItem
#     extra = 1  # Number of empty forms to display by default

# class CartAdmin(admin.ModelAdmin):
#     """
#     Admin view for Cart model.
#     """
#     list_display = ('id', 'user', 'session_id', 'created_at', 'updated_at')
#     search_fields = ['user__username', 'session_id']
#     list_filter = ['created_at', 'updated_at']
#     inlines = [CartItemInline]

#     # Optional: You can add filters for cart items or stock-related actions if needed

# class CartItemAdmin(admin.ModelAdmin):
#     """
#     Admin view for CartItem model.
#     """
#     list_display = ('cart', 'product', 'variant', 'quantity', 'created_at', 'updated_at')
#     search_fields = ['product__name', 'variant__sku']
#     list_filter = ['created_at', 'updated_at']
#     raw_id_fields = ('product', 'variant')  # To use a lookup field for Product and Variant

#     def product(self, obj):
#         return obj.product.name

#     def variant(self, obj):
#         return obj.variant.sku if obj.variant else None

# # Register models
# admin.site.register(Cart, CartAdmin)
# admin.site.register(CartItem, CartItemAdmin)
