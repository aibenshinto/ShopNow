from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import razorpay
from cart_app.models import Cart
from payment_app.models import RazorpayOrder
from django.conf import settings
from .serializers import TransactionHistorySerializer
from authentication_app.models import Customer
from django.conf import settings
# API to verify the Razorpay payment
class VerifyPaymentAPIView(APIView):
    def post(self, request):
        try:
            data = request.data

            razorpay_order_id = data.get("razorpay_order_id")
            razorpay_payment_id = data.get("razorpay_payment_id")
            razorpay_signature = data.get("razorpay_signature")

            if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
                return Response({"error": "Missing required parameters."}, status=status.HTTP_400_BAD_REQUEST)

            razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

            # Verify payment signature
            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature
            }

            # Verify the payment signature using Razorpay's utility method
            razorpay_client.utility.verify_payment_signature(params_dict)

            # Get the Razorpay order by order_id
            razorpay_order = RazorpayOrder.objects.get(order_id=razorpay_order_id)

            # Update the payment details and status
            razorpay_order.payment_id = razorpay_payment_id
            razorpay_order.payment_status = "paid"
            razorpay_order.save()

            return Response({"message": "Payment verified successfully."}, status=status.HTTP_200_OK)

        except razorpay.errors.SignatureVerificationError as e:
            return Response({"error": f"Signature verification failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except RazorpayOrder.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# View to render the Razorpay checkout page
def checkout_view(request, cart_id):
    """
    View to render the Razorpay checkout page.
    """
    
    # Get the cart details by cart_id
    cart = get_object_or_404(Cart, id=cart_id)
    
    # You can pass additional cart details if needed (e.g., cart items, total, etc.)
    return render(request, 'checkout.html', {'cart_id': cart.id, 'total_price': cart.calculate_total(), 'razorpay_key': settings.RAZORPAY_KEY_ID})


# View to render order confirmation page
def order_confirmation(request):
    return render(request, 'order_confirmation.html')


# API to retrieve payment details for a cart
class RetrievePaymentDetailsAPIView(APIView):
    def get(self, request, cart_id):
        try:
            cart = get_object_or_404(Cart, id=cart_id)

            # Get the Razorpay order for the cart
            razorpay_order = RazorpayOrder.objects.get(cart=cart)

            return Response({
                "razorpay_order_id": razorpay_order.order_id,
                "razorpay_payment_id": razorpay_order.payment_id,
                "payment_status": razorpay_order.payment_status,
                "total_price": cart.calculate_total(),
                "currency": "INR"
            }, status=status.HTTP_200_OK)

        except RazorpayOrder.DoesNotExist:
            return Response({"error": "No Razorpay order found for this cart."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# API to retrieve transaction history
class TransactionHistoryAPIView(APIView):
    def get(self, request):
        """
        Get the transaction history (cart ID, order ID, payment ID, payment status).
        """
        try:
            # Get all carts with associated payment details (order_id, payment_id, status)
            carts = Cart.objects.filter(razorpayorder__isnull=False)  # Make sure you have related payment info

            # Serialize the carts with transaction data
            serializer = TransactionHistorySerializer(carts, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
# API to create a Razorpay order for a cart
class CreateRazorpayOrderAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Retrieve the customer associated with the authenticated user
            try:
                customer = Customer.objects.get(user=request.user)
            except Customer.DoesNotExist:
                return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)

            # Get the active cart associated with the customer
            cart = Cart.objects.filter(customer=customer).first()  # Assuming one active cart per user
            if not cart:
                return Response({"error": "No active cart found for the user."}, status=status.HTTP_404_NOT_FOUND)

            # Calculate the total amount for the cart
            total = cart.calculate_total()

            # Check if total is valid
            if total <= 0:
                return Response({"error": "Cart total must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)

            # Initialize Razorpay client with credentials from settings
            razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

            # Create a new Razorpay order
            razorpay_order = razorpay_client.order.create({
                "amount": int(total * 100),  # Razorpay expects amount in paise (100 paise = 1 INR)
                "currency": "INR",
                "payment_capture": "1"
            })

            # Save the Razorpay order with the cart association
            RazorpayOrder.objects.create(cart=cart, order_id=razorpay_order['id'])

            return Response({
                "razorpay_order_id": razorpay_order['id'],
                "total_price": total,
                "currency": "INR",
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


