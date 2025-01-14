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
from .models import Category
from .serializers import CategorySerializer
from authentication_app.models import Vendor





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







class VendorCategoryListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Check if the logged-in user is a vendor
        if hasattr(request.user, 'vendor_profile'):
            vendor = request.user.vendor_profile
            categories = Category.objects.filter(vendor=vendor)
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Access denied. User is not authorized."}, status=status.HTTP_403_FORBIDDEN)

    def post(self, request):
        # Check if the logged-in user is a vendor
        if hasattr(request.user, 'vendor_profile'):
            vendor = request.user.vendor_profile
            data = request.data
            data['vendor'] = vendor.id  # Associate the category with the vendor
            serializer = CategorySerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Access denied. User is not authorized."}, status=status.HTTP_403_FORBIDDEN)

class VendorCategoryDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, category_id):
        if hasattr(request.user, 'vendor_profile'):
            vendor = request.user.vendor_profile
            try:
                category = Category.objects.get(id=category_id, vendor=vendor)
                serializer = CategorySerializer(category)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Category.DoesNotExist:
                return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error": "Access denied. User is not authorized."}, status=status.HTTP_403_FORBIDDEN)

    def put(self, request, category_id):
        if hasattr(request.user, 'vendor_profile'):
            vendor = request.user.vendor_profile
            try:
                category = Category.objects.get(id=category_id, vendor=vendor)
                serializer = CategorySerializer(category, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Category.DoesNotExist:
                return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error": "Access denied. User is not authorized."}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, category_id):
        if hasattr(request.user, 'vendor_profile'):
            vendor = request.user.vendor_profile
            try:
                category = Category.objects.get(id=category_id, vendor=vendor)
                category.delete()
                return Response({"message": "Category deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
            except Category.DoesNotExist:
                return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error": "Access denied. User is not authorized."}, status=status.HTTP_403_FORBIDDEN)