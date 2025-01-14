from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from admin_panel.serializers import CustomerUpdateSerializer, VendorUpdateSerializer
from authentication_app.models import Vendor, Customer
from authentication_app.serializers import VendorSerializer, CustomerSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication

class AdminRestrictedView(APIView):
    """
    Base view for admin-restricted actions. Checks if the username is 'admin'.
    """
    authentication_classes = [JWTAuthentication]  # Specify JWTAuthentication here
    permission_classes = [IsAuthenticated]

    def is_admin(self, user):
        return user.is_authenticated and user.username == "admin"


# Vendor API View
class VendorListCreateAPIView(AdminRestrictedView):
    def get(self, request):
        if not self.is_admin(request.user):
            return Response({"error": "Unauthorized access."}, status=status.HTTP_403_FORBIDDEN)
        
        vendors = Vendor.objects.all()
        serializer = VendorSerializer(vendors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if not self.is_admin(request.user):
            return Response({"error": "Unauthorized access."}, status=status.HTTP_403_FORBIDDEN)

        serializer = VendorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerListCreateAPIView(AdminRestrictedView):
    def get(self, request):
        if not self.is_admin(request.user):
            return Response({"error": "Unauthorized access."}, status=status.HTTP_403_FORBIDDEN)
        
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if not self.is_admin(request.user):
            return Response({"error": "Unauthorized access."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Vendor Update API View
class VendorRetrieveUpdateDestroyAPIView(AdminRestrictedView):
    def get(self, request, pk):
        if not self.is_admin(request.user):
            return Response({"error": "Unauthorized access."}, status=status.HTTP_403_FORBIDDEN)

        try:
            vendor = Vendor.objects.get(pk=pk)
        except Vendor.DoesNotExist:
            return Response({"error": "Vendor not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer =  VendorUpdateSerializer(vendor)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        if not self.is_admin(request.user):
            return Response({"error": "Unauthorized access."}, status=status.HTTP_403_FORBIDDEN)

        try:
            vendor = Vendor.objects.get(pk=pk)
        except Vendor.DoesNotExist:
            return Response({"error": "Vendor not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = VendorUpdateSerializer(vendor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not self.is_admin(request.user):
            return Response({"error": "Unauthorized access."}, status=status.HTTP_403_FORBIDDEN)

        try:
            vendor = Vendor.objects.get(pk=pk)
        except Vendor.DoesNotExist:
            return Response({"error": "Vendor not found."}, status=status.HTTP_404_NOT_FOUND)

        vendor.delete()
        return Response({"message": "Vendor deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# Customer Update API View
class CustomerRetrieveUpdateDestroyAPIView(AdminRestrictedView):
    def get(self, request, pk):
        if not self.is_admin(request.user):
            return Response({"error": "Unauthorized access."}, status=status.HTTP_403_FORBIDDEN)

        try:
            customer = Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CustomerUpdateSerializer(customer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        if not self.is_admin(request.user):
            return Response({"error": "Unauthorized access."}, status=status.HTTP_403_FORBIDDEN)

        try:
            customer = Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CustomerUpdateSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not self.is_admin(request.user):
            return Response({"error": "Unauthorized access."}, status=status.HTTP_403_FORBIDDEN)

        try:
            customer = Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)

        customer.delete()
        return Response({"message": "Customer deleted successfully."}, status=status.HTTP_204_NO_CONTENT)