from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('product_app/',include('product_app.urls')),
    path('', include('order.urls')),  # Include the orders app URLs
    path('', include('cart_app.urls')),  # Replace 'your_app_name' with your app's name
    path('', include('authentication_app.urls')),
    path('accounts/', include('allauth.urls'))
]
