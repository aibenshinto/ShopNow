from django.urls import path
from .views import CreateOrderView, OrderDetailView, OrderHistoryView, UpdateOrderStatusView

urlpatterns = [
    path('create/', CreateOrderView.as_view(), name='create_order'),
    path('history/', OrderHistoryView.as_view(), name='order_history'),
    path('<str:order_id>/update-status/', UpdateOrderStatusView.as_view(), name='update_order_status'),
    path('<str:order_id>/', OrderDetailView.as_view(), name='order_detail'),
]
