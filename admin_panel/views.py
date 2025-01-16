from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from rest_framework.permissions import IsAuthenticated
from admin_panel.serializers import CustomerUpdateSerializer, VendorUpdateSerializer
from authentication_app.models import Vendor, Customer
from authentication_app.serializers import VendorSerializer, CustomerSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from product_app.models import ProductVariant,ProductVariantAttribute
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from product_app.serializers import ProductVariantAttributeSerializer

CUSTOMER_NOT_FOUND = "Customer not found."
VENDOR_NOT_FOUND = "Vendor not found."
UNAUTHORIZED_ACCESS = "Unauthorized access."

class AdminRestrictedView(APIView):
    """
    Base view for admin-restricted actions. Checks if the user is staff.
    """
    authentication_classes = [JWTAuthentication]  # Specify JWTAuthentication here
    permission_classes = [IsAuthenticated]

    def is_staff(self, user):
        return user.is_authenticated and user.is_staff
   

class ProductVariantAttributeListAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        if request.user.is_authenticated and request.user.is_staff:
            # Fetch all product variant attributes
            product_variant_attributes = ProductVariantAttribute.objects.all()
            # Serialize the data
            serializer = ProductVariantAttributeSerializer(product_variant_attributes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"error": "Unauthorized access."},
            status=status.HTTP_403_FORBIDDEN
        )

# Vendor API View
class VendorListCreateAPIView(AdminRestrictedView):
    """
    API view to list and create vendors. Only approved vendors are listed.
    """
    def get(self, request):
        if not self.is_staff(request.user):
            return Response({"error": VENDOR_NOT_FOUND}, status=status.HTTP_403_FORBIDDEN)
        
        # Filter to include only approved vendors
        approved_vendors = Vendor.objects.filter(is_approved=True)
        serializer = VendorSerializer(approved_vendors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if not self.is_staff(request.user):
            return Response({"error": UNAUTHORIZED_ACCESS }, status=status.HTTP_403_FORBIDDEN)

        serializer = VendorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerListCreateAPIView(AdminRestrictedView):
    def get(self, request):
        if not self.is_staff(request.user):
            return Response({"error": UNAUTHORIZED_ACCESS}, status=status.HTTP_403_FORBIDDEN)
        
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if not self.is_staff(request.user):
            return Response({"error": UNAUTHORIZED_ACCESS}, status=status.HTTP_403_FORBIDDEN)

        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Vendor Update API View
class VendorRetrieveUpdateDestroyAPIView(AdminRestrictedView):
    def get(self, request, pk):
        if not self.is_staff(request.user):
            return Response({"error": UNAUTHORIZED_ACCESS}, status=status.HTTP_403_FORBIDDEN)

        try:
            vendor = Vendor.objects.get(pk=pk)
        except Vendor.DoesNotExist:
            return Response({"error": VENDOR_NOT_FOUND }, status=status.HTTP_404_NOT_FOUND)

        serializer = VendorUpdateSerializer(vendor)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        if not self.is_staff(request.user):
            return Response({"error": UNAUTHORIZED_ACCESS }, status=status.HTTP_403_FORBIDDEN)

        try:
            vendor = Vendor.objects.get(pk=pk)
        except Vendor.DoesNotExist:
            return Response({"error": VENDOR_NOT_FOUND }, status=status.HTTP_404_NOT_FOUND)

        serializer = VendorUpdateSerializer(vendor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not self.is_staff(request.user):
            return Response({"error": UNAUTHORIZED_ACCESS }, status=status.HTTP_403_FORBIDDEN)

        try:
            vendor = Vendor.objects.get(pk=pk)
        except Vendor.DoesNotExist:
            return Response({"error": VENDOR_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)

        vendor.delete()
        return Response({"message": "Vendor deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

# Customer Update API View
class CustomerRetrieveUpdateDestroyAPIView(AdminRestrictedView):
    def get(self, request, pk):
        if not self.is_staff(request.user):
            return Response({"error": UNAUTHORIZED_ACCESS }, status=status.HTTP_403_FORBIDDEN)

        try:
            customer = Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return Response({"error":CUSTOMER_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)

        serializer = CustomerUpdateSerializer(customer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        if not self.is_staff(request.user):
            return Response({"error": UNAUTHORIZED_ACCESS }, status=status.HTTP_403_FORBIDDEN)

        try:
            customer = Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return Response({"error": CUSTOMER_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)

        serializer = CustomerUpdateSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not self.is_staff(request.user):
            return Response({"error": UNAUTHORIZED_ACCESS }, status=status.HTTP_403_FORBIDDEN)

        try:
            customer = Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return Response({"error": CUSTOMER_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)

        customer.delete()
        return Response({"message": "Customer deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
class PendingAccountsAPIView(AdminRestrictedView):
    """
    API to fetch all pending vendors and customers awaiting approval.
    """
    def get(self, request):
        if not self.is_staff(request.user):
            return Response({"error": UNAUTHORIZED_ACCESS }, status=status.HTTP_403_FORBIDDEN)

        pending_vendors = Vendor.objects.filter(is_approved=False)
     
        vendor_serializer = VendorSerializer(pending_vendors, many=True)
     

        return Response({
            "pending_vendors": vendor_serializer.data,
          
        }, status=status.HTTP_200_OK)

class ApproveVendorAPIView(AdminRestrictedView):
    """
    API to approve a vendor.
    """
    def patch(self, request, pk):
        if not self.is_staff(request.user):
            return Response({"error": "Unauthorized access."}, status=status.HTTP_403_FORBIDDEN)

        try:
            vendor = Vendor.objects.get(pk=pk)
        except Vendor.DoesNotExist:
            return Response({"error": VENDOR_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)

        vendor.is_approved = True
        vendor.save()
        return Response({"message": f"Vendor '{vendor.user}' has been approved."}, status=status.HTTP_200_OK)

