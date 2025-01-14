from django.urls import path
from .views import VendorDashboardView
from .views import VendorDashboardView, VendorCategoryListCreateView, VendorCategoryDetailView

urlpatterns = [
    path('dashboard/', VendorDashboardView.as_view(), name='vendor_dashboard'),
    path('categories/', VendorCategoryListCreateView.as_view(), name='vendor_category_list_create'),
    path('categories/<int:category_id>/', VendorCategoryDetailView.as_view(), name='vendor_category_detail'),
]