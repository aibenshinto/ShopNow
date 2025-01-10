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
    path('review/',include('reviews.urls')),
    path('', include('order.urls')),  # Include the orders app URLs
    path('', include('cart_app.urls')),  # Replace 'your_app_name' with your app's name
    path('api/', include('shippinaddress.urls')),
    path('favicon.ico', serve, {'path': 'favicon.ico'}),  # Serve favicon.ico as static
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

