from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from authentication_app.models import Vendor
from order.models import Order
from order.serializers import OrderSerializer
from decimal import Decimal
from django.db.models import Sum
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
class VendorDashboardView(APIView):
    authentication_classes = [JWTAuthentication]  # Specify JWTAuthentication here
    permission_classes = [IsAuthenticated] 
    def get(self, request):
        # Check if the logged-in user is a vendor or customer
        if hasattr(request.user, 'vendor_profile'):
            # Vendor logic
            vendor_email = request.user.vendor_profile.vendor_email
            orders = Order.objects.filter(vendor_email=vendor_email)
            total_sales = orders.aggregate(total_sales=Sum('total_price'))['total_sales'] or 0
            earnings = self.calculate_earnings(total_sales)
            admin_commission = self.calculate_admin_commission(total_sales)

            dashboard_data = {
                "total_orders": orders.count(),
                "total_sales": total_sales,
                "earnings": earnings,
                "admin_commission": admin_commission,
                "orders": OrderSerializer(orders, many=True).data,
            }
            return Response(dashboard_data, status=status.HTTP_200_OK)

        elif hasattr(request.user, 'customer_profile'):
            # Customers cannot access vendor dashboard
            return Response(
                {"error": "Access denied. Customers cannot access the vendor dashboard."},
                status=status.HTTP_403_FORBIDDEN,
            )

        else:
            # User is neither a vendor nor a customer
            return Response(
                {"error": "Access denied. User is not authorized."},
                status=status.HTTP_403_FORBIDDEN,
            )

    def calculate_earnings(self, total_sales):
        commission_rate = Decimal(0.10)  # 10% admin commission
        return total_sales * (Decimal(1) - commission_rate)

    def calculate_admin_commission(self, total_sales):
        commission_rate = Decimal(0.10)  # 10% admin commission
        return total_sales * commission_rate
