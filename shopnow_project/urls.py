from django.contrib import admin
from django.urls import path,include
from django.contrib.staticfiles.views import serve
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('authentication_app.urls')),
    path('accounts/', include('allauth.urls')),
    path('product_app/',include('product_app.urls')),
<<<<<<< HEAD
    path('review/',include('reviews.urls')),
=======
    path('orders/', include('order.urls')), 
    path('vendor/', include('vendor.urls')),
    path('', include('cart_app.urls')),  # Replace 'your_app_name' with your app's name
    path('', include('admin_panel.urls')),
    path('accounts/', include('allauth.urls')),
    path('product_app/',include('product_app.urls')),
>>>>>>> 088fd83c1a22ee0c7329756b6547b95e63685e74
    path('', include('order.urls')),  # Include the orders app URLs
    path('', include('cart_app.urls')),  # Replace 'your_app_name' with your app's name
    path('api/', include('shippinaddress.urls')),
    path('favicon.ico', serve, {'path': 'favicon.ico'}),  # Serve favicon.ico as static
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

