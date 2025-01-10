from django.urls import path
from . import views
# from .views import create_shipping_address,TestView
urlpatterns = [
    # Add to Cart
    path('api/add-to-cart/', views.add_to_cart, name='add_to_cart'),

    # Checkout
    path('api/checkout/', views.checkout, name='checkout'),

    # View Cart
    path('view-cart/<int:user_id>/', views.view_cart, name='view_cart'),  # For authenticated users
    path('view-cart/<str:session_id>/', views.view_cart, name='view_cart_guest'),  # For guest users
    path('cart/delete/', views.delete_from_cart, name='delete_from_cart'),
#   path('shipping-address/', AddShippingAddressView.as_view(), name='add_shipping_address'),
#   path('create-shipping-address/', views.create_shipping_address, name='create_shipping_address'),
#   path('test/', TestView.as_view(), name='test'),
]
     

