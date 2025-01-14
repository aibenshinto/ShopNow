from django.urls import path
from .views import ReviewAPIView, ReplyAPIView

urlpatterns = [
    path('reviews/<int:product_variant_id>/', ReviewAPIView.as_view(), name='reviews'),
    path('reply/<int:review_id>/', ReplyAPIView.as_view(), name='reply'),
]
