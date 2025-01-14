
from django.http import HttpResponse
from django.urls import path
from .views import  HomePageView, LogoutView, RegisterVendor, RegisterCustomer, Login, UpdateCustomerProfile,  UpdateVendorProfileView
from . import views

urlpatterns = [
    path('register/vendor/', RegisterVendor.as_view(), name='register_vendor'),
    path('register/customer/', RegisterCustomer.as_view(), name='register_customer'),
    path('login/', Login.as_view(), name='login'),
    path('home/', HomePageView.as_view(), name='home'),  # Home page after login
    path('profile/vendor/', UpdateVendorProfileView.as_view(), name='update_vendor_profile'),
    path('profile/customer/', UpdateCustomerProfile.as_view(), name='update_customer_profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
