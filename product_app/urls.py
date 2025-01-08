from django.urls import path
from .views import ProductCreateView

urlpatterns = [
    path('api/products/', ProductCreateView.as_view(), name='create-product'),
]
