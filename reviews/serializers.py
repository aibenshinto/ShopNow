from rest_framework import serializers
from .models import Review, Reply

class ReplySerializer(serializers.ModelSerializer):
    vendor = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Reply
        fields = ['id', 'review', 'vendor', 'reply_text', 'created_at', 'updated_at']
        read_only_fields = ['vendor', 'created_at', 'updated_at']


class ReviewSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField(read_only=True)
    product_variant = serializers.StringRelatedField(read_only=True)
    reply = serializers.SerializerMethodField() 

    class Meta:
        model = Review
        fields = ['id', 'product_variant', 'customer', 'rating', 'review_text', 'reply', 'created_at', 'updated_at']
        read_only_fields = ['customer', 'created_at', 'updated_at']
    
    def get_reply(self, obj):
        reply = Reply.objects.filter(review=obj).order_by('-created_at').first()
        if reply:
            return ReplySerializer(reply).data
        return None