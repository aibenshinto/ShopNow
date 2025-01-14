from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import AddressBook
from .serializers import AddressBookSerializer, AddressBookCreateSerializer
from django.contrib.auth.models import User

# Helper function to get user or return None
def get_user_or_404(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None

class UserAddressListCreateView(APIView):
    """
    Handles listing all addresses for a specific user and creating a new address.
    """
    def get(self, request, user_id, *args, **kwargs):
        user = get_user_or_404(user_id)
        if not user:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        addresses = AddressBook.objects.filter(user=user)
        serializer = AddressBookSerializer(addresses, many=True)
        return Response(serializer.data)

    def post(self, request, user_id, *args, **kwargs):
        user = get_user_or_404(user_id)
        if not user:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AddressBookCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserAddressDetailView(APIView):
    """
    Handles retrieving, updating, and deleting a specific address for a specific user.
    """
    def get(self, request, user_id, address_id, *args, **kwargs):
        user = get_user_or_404(user_id)
        if not user:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        address = get_object_or_404(AddressBook, id=address_id, user=user)
        serializer = AddressBookSerializer(address)
        return Response(serializer.data)

    def put(self, request, user_id, address_id, *args, **kwargs):
        user = get_user_or_404(user_id)
        if not user:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        address = get_object_or_404(AddressBook, id=address_id, user=user)
        serializer = AddressBookCreateSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id, address_id, *args, **kwargs):
        user = get_user_or_404(user_id)
        if not user:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        address = get_object_or_404(AddressBook, id=address_id, user=user)
        address.delete()
        return Response({"message": "Address deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
