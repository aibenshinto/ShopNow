from django.urls import path
from .views import AddToCartView, CheckoutView, ViewCartView, DeleteFromCartView

urlpatterns = [
    path('api/add-to-cart/', AddToCartView.as_view(), name='add_to_cart'),
    path('api/checkout/', CheckoutView.as_view(), name='checkout'),
    path('api/view-cart/', ViewCartView.as_view(), name='view_cart'),
    path('api/cart/delete/', DeleteFromCartView.as_view(), name='delete_from_cart'),
]
