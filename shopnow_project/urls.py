from django.contrib import admin
<<<<<<< HEAD
from django.urls import path, include  # Include the include function

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('order.urls')),  # Include the orders app URLs
=======
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('cart_app.urls')),  # Replace 'your_app_name' with your app's name
>>>>>>> 2276ac905e619c9f8b92ea28932781b55fe7f8af
]
