from django.urls import path
<<<<<<< HEAD
from .views import  checkout_view, order_confirmation, RetrievePaymentDetailsAPIView, TransactionHistoryAPIView, CreateRazorpayOrderAPIView,ReorderCreateRazorpayOrderAPIView
=======
from .views import  checkout_view, order_confirmation, RetrievePaymentDetailsAPIView, TransactionHistoryAPIView, CreateRazorpayOrderAPIView,VerifyPaymentAPIView
>>>>>>> 4dead17b917f6bd1304b264106da7907bc9df2c9

urlpatterns = [
    # path('verify_payment/', VerifyPaymentAPIView.as_view(), name='verify_payment'),
    path('checkout/<int:cart_id>/', checkout_view, name='checkout'),
    path('order_confirmation/', order_confirmation, name='order_confirmation'),
    path('payment-details/<str:payment_id>/', RetrievePaymentDetailsAPIView.as_view(), name='payment-details'),
    path('transaction_history/', TransactionHistoryAPIView.as_view(), name='transaction_history'),
    path('create-razorpay-order/', CreateRazorpayOrderAPIView.as_view(), name='create-razorpay-order'),
<<<<<<< HEAD
    path('create-razorpay-reorder/<str:order_id>/', ReorderCreateRazorpayOrderAPIView.as_view(), name='reorder-create'),
=======
     path('payment/verify/', VerifyPaymentAPIView.as_view(), name='verify_payment'),
      path('order-confirmation/', order_confirmation, name='order_confirmation'),
>>>>>>> 4dead17b917f6bd1304b264106da7907bc9df2c9
]
