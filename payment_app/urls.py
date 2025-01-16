from django.urls import path
from .views import  checkout_view, order_confirmation, RetrievePaymentDetailsAPIView, TransactionHistoryAPIView, CreateRazorpayOrderAPIView,VerifyPaymentAPIView

urlpatterns = [
    # path('verify_payment/', VerifyPaymentAPIView.as_view(), name='verify_payment'),
    path('checkout/<int:cart_id>/', checkout_view, name='checkout'),
    path('order_confirmation/', order_confirmation, name='order_confirmation'),
    path('payment-details/<str:payment_id>/', RetrievePaymentDetailsAPIView.as_view(), name='payment-details'),
    path('transaction_history/', TransactionHistoryAPIView.as_view(), name='transaction_history'),
    path('create-razorpay-order/', CreateRazorpayOrderAPIView.as_view(), name='create-razorpay-order'),
     path('payment/verify/', VerifyPaymentAPIView.as_view(), name='verify_payment'),
      path('order-confirmation/', order_confirmation, name='order_confirmation'),
]
