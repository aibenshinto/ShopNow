from django.urls import path
from .views import  ProductAPIView, AttributeAPIView, AttributeValueAPIView, ProductVariantAPIView, ProductVariantAttributeAPIView,ProductVariantAttributeCreateAPIView, product_variants_list, ProductVariantAttributeSearchAPIView

urlpatterns = [
    path('products/', ProductAPIView.as_view(), name='product-list'),
    path('attributes/', AttributeAPIView.as_view(), name='attribute-list'),
    path('attribute-values/', AttributeValueAPIView.as_view(), name='attribute-value-list'),
    path('product-variants/', ProductVariantAPIView.as_view(), name='product-variant-list'),
    path('product-variant-attributes/', ProductVariantAttributeAPIView.as_view(), name='product-variant-attribute-list'),
    path('product-variant-attributes/<int:pk>/', ProductVariantAttributeAPIView.as_view(), name='product-variant-attribute-detail'),
    path('product-variant-attribute/create/', ProductVariantAttributeCreateAPIView.as_view(), name='product-variant-attribute-create'),
    path('product-variant-attributes/search/', ProductVariantAttributeSearchAPIView.as_view(), name='product-variant-attributes-search'),
    path('product-variants-list/', product_variants_list, name='product-variants-list'),
]
