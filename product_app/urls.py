from django.urls import path
from .views import  ProductAPIView, AttributeAPIView, AttributeValueAPIView, ProductVariantAPIView, ProductVariantAttributeAPIView

urlpatterns = [
    path('products/', ProductAPIView.as_view(), name='product-list'),
    path('attributes/', AttributeAPIView.as_view(), name='attribute-list'),
    path('attribute-values/', AttributeValueAPIView.as_view(), name='attribute-value-list'),
    path('product-variants/', ProductVariantAPIView.as_view(), name='product-variant-list'),
    path('product-variant-attributes/', ProductVariantAttributeAPIView.as_view(), name='product-variant-attribute-list'),
]
