from django.urls import path
from .views import UserAddressListCreateView, UserAddressDetailView

urlpatterns = [
    path('users/<int:user_id>/addresses/', UserAddressListCreateView.as_view(), name='user-address-list-create'),
    path('users/<int:user_id>/addresses/<int:address_id>/', UserAddressDetailView.as_view(), name='user-address-detail'),
]
