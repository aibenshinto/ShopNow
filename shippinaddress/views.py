from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from authentication_app.models import Customer  # Import the Customer model
from .models import AddressBook
from .serializers import AddressBookSerializer, AddressBookCreateSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
class UserAddressListCreateView(APIView):
    """
    Handles listing all addresses for the authenticated user and creating a new address.
    """
    authentication_classes = [JWTAuthentication]  # Or JWTAuthentication if you're using JWT
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        print(f"Authenticated user: {request.user}") 
        try:
            # Ensure we retrieve the Customer instance
            customer = Customer.objects.get(user=request.user)  # Query the Customer model
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the addresses for the logged-in customer
        addresses = AddressBook.objects.filter(user=request.user)
        serializer = AddressBookSerializer(addresses, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        try:
            # Ensure we retrieve the Customer instance
            customer = Customer.objects.get(user=request.user)  # Query the Customer model
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AddressBookCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customer=customer)  # Save the address with the authenticated user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserAddressDetailView(APIView):
    """
    Handles retrieving, updating, and deleting a specific address for the authenticated user.
    """
    authentication_classes = [JWTAuthentication]  # Or JWTAuthentication if you're using JWT
    permission_classes = [IsAuthenticated]

    def get(self, request, address_id, *args, **kwargs):
        
        try:
            # Ensure we retrieve the Customer instance
            customer = Customer.objects.get(user=request.user)  # Query the Customer model
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the address for the logged-in customer
        address = get_object_or_404(AddressBook, id=address_id, user=request.user)
        serializer = AddressBookSerializer(address)
        return Response(serializer.data)

    def put(self, request, address_id, *args, **kwargs):
        try:
            # Ensure we retrieve the Customer instance
            customer = Customer.objects.get(user=request.user)  # Query the Customer model
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the address for the logged-in customer
        address = get_object_or_404(AddressBook, id=address_id, user=request.user)
        serializer = AddressBookCreateSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, address_id, *args, **kwargs):
        try:
            # Ensure we retrieve the Customer instance
            customer = Customer.objects.get(user=request.user)  # Query the Customer model
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the address for the logged-in customer
        address = get_object_or_404(AddressBook, id=address_id, user=request.user)
        address.delete()
        return Response({"message": "Address deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

