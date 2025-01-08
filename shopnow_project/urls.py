from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('product_app/',include('product_app.urls')),
    # path('', include('order.urls')),  # Include the orders app URLs
    # path('', include('cart_app.urls')),  # Replace 'your_app_name' with your app's name
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)