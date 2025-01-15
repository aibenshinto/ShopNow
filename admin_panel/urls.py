from django.urls import path
from .views import  ApproveVendorAPIView, CustomerRetrieveUpdateDestroyAPIView, PendingAccountsAPIView, VendorListCreateAPIView,CustomerListCreateAPIView, VendorRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('vendors/', VendorListCreateAPIView.as_view(), name='vendor-list-create'),
    path('customers/', CustomerListCreateAPIView.as_view(), name='customer-list-create'),
    path('vendor/<int:pk>/', VendorRetrieveUpdateDestroyAPIView.as_view(), name='vendor-retrieve-update-destroy'),
    path('customer/<int:pk>/', CustomerRetrieveUpdateDestroyAPIView.as_view(), name='customer-retrieve-update-destroy'),
    path('accounts/pending/', PendingAccountsAPIView.as_view(), name='pending_accounts'),
    path('vendors/<int:pk>/approve/', ApproveVendorAPIView.as_view(), name='approve-vendor'),
    
]