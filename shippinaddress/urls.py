from django.urls import path
from .views import UserAddressListCreateView, UserAddressDetailView

urlpatterns = [
    # List and create addresses for the logged-in user
    path('api/addresses/', UserAddressListCreateView.as_view(), name='address-list-create'),
    
    # Retrieve, update, and delete a specific address for the logged-in user
    path('api/address/<int:address_id>/', UserAddressDetailView.as_view(), name='address-detail'),
]
