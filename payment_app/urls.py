from django.urls import path
from .views import  checkout_view, order_confirmation, RetrievePaymentDetailsAPIView, TransactionHistoryAPIView, CreateRazorpayOrderAPIView,ReorderCreateRazorpayOrderAPIView

urlpatterns = [
    # path('verify_payment/', VerifyPaymentAPIView.as_view(), name='verify_payment'),
    path('checkout/<int:cart_id>/', checkout_view, name='checkout'),
    path('order_confirmation/', order_confirmation, name='order_confirmation'),
    path('retrieve_payment_details/<int:cart_id>/', RetrievePaymentDetailsAPIView.as_view(), name='retrieve_payment_details'),
    path('transaction_history/', TransactionHistoryAPIView.as_view(), name='transaction_history'),
    path('create-razorpay-order/', CreateRazorpayOrderAPIView.as_view(), name='create-razorpay-order'),
    path('create-razorpay-reorder/<str:order_id>/', ReorderCreateRazorpayOrderAPIView.as_view(), name='reorder-create'),
]
