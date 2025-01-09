from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .models import Vendor, Customer
from .serializers import VendorSerializer, CustomerSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login
from django.http import HttpResponse
from .models import Vendor, Customer
from social_django.models import UserSocialAuth

# Generate JWT tokens
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# Register Vendor
class RegisterVendor(APIView):
    def get(self, request):
        # Render the vendor registration form
        return render(request, 'register_vendor.html')

    def post(self, request):
            print('==========',request.data)
            # Handle the form data (request.POST) instead of request.data
            serializer = VendorSerializer(data=request.data)  # Use request.POST for form data
            if serializer.is_valid():
                # Create user instance using validated data
                user_data = serializer.validated_data.pop('user')
                print('*******8',user_data)  # Assuming your serializer handles 'user' data
                user = User.objects.create_user(**user_data)
                print('$$$$4',user)
                # Create Vendor instance
                Vendor.objects.create(user=user, **serializer.validated_data)

                return redirect('login')  # Redirect to login page after successful registration
            else:
                print(serializer.errors)
            return render(request, 'register_vendor.html', {'errors': serializer.errors})  # Re-render form with errors if validation fails

# Register Customer
class RegisterCustomer(APIView):
    def get(self, request):
        # Render the customer registration form
        return render(request, 'register_customer.html')

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            user_data = serializer.validated_data.pop('user')
            user = User.objects.create_user(**user_data)
            Customer.objects.create(user=user, **serializer.validated_data)
            return redirect('login')  # Redirect to the login page after successful registration
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class Login(APIView):
    def get(self, request):
        # Render the customer registration form
        return render(request, 'login.html')
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username:
            return Response({"detail": "Username is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not password:
            return Response({"detail": "Password is required."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        
        
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })

        # if user:
        #     refresh = RefreshToken.for_user(user)
        #     response_data = {
        #         'access': str(refresh.access_token),
        #         'refresh': str(refresh),
        #     }
        #     # Store the token in session or redirect as needed
        #     request.session['access_token'] = response_data['access']
        #     #return redirect('home')  # Redirect to home page after successful login

        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    

# Home Page
class HomePageView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        # Render the home page
        return render(request, 'home.html')

class UpdateVendorProfileView(APIView):
    def put(self, request):
        try:
            # Assuming the vendor is authenticated and identified via request.user
            vendor = Vendor.objects.get(user=request.user)
            serializer = VendorSerializer(vendor, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Vendor profile updated successfully."}, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Vendor.DoesNotExist:
            return Response({"error": "Vendor profile not found."}, status=status.HTTP_404_NOT_FOUND)

# Update Customer Profile
class UpdateCustomerProfile(APIView):
    def put(self, request):
        try:
            # Assuming the customer is authenticated and identified via request.user
            customer = Customer.objects.get(user=request.user)
            serializer = CustomerSerializer(customer, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Customer profile updated successfully."}, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Customer.DoesNotExist:
            return Response({"error": "Customer profile not found."}, status=status.HTTP_404_NOT_FOUND)
class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                # Blacklisting the refresh token to effectively log out the user
                token.blacklist()
                return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
            return Response({"detail": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)