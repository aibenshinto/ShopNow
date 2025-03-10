from django.urls import path
from . import views

urlpatterns = [
    # Add to Cart
    path('api/add-to-cart/', views.add_to_cart, name='add_to_cart'),

    # Checkout
    path('api/checkout/', views.checkout, name='checkout'),

    # View Cart
     path('view-cart/<int:user_id>/', views.view_cart, name='view_cart'),  # For authenticated users
    path('view-cart/<str:session_id>/', views.view_cart, name='view_cart_guest'),  # For guest users
 

]