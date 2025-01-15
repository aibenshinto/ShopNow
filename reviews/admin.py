from django.contrib import admin
from .models import Review, Reply

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product_variant', 'customer', 'rating', 'created_at', 'updated_at')
    search_fields = ('customer__customer_name', 'product_variant__sku', 'review_text')
    list_filter = ('rating', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('review', 'vendor', 'reply_text', 'created_at', 'updated_at')
    search_fields = ('vendor__vendor_name', 'reply_text')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')