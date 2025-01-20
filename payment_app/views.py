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
import uuid
from django.utils.timezone import now
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
    """
    API view to retrieve payment details using the Razorpay order ID.
    """

    def get(self, request, payment_id):
        try:
            # Get the Razorpay order using the Razorpay order ID
            razorpay_order = get_object_or_404(RazorpayOrder, payment_id=payment_id)

            # Get the associated cart
            cart = razorpay_order.cart

            return Response({
                "razorpay_order_id": razorpay_order.order_id,
                "razorpay_payment_id": razorpay_order.payment_id,
                "payment_status": razorpay_order.payment_status,
                "total_price": cart.calculate_total(),
                "currency": "INR"
            }, status=status.HTTP_200_OK)

        except RazorpayOrder.DoesNotExist:
            return Response({"error": "No Razorpay order found for this ID."}, status=status.HTTP_404_NOT_FOUND)
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
# API to create a Razorpay order for a cart
from django.core.mail import send_mail
from authentication_app.models import Vendor
from django.core.mail import send_mail
from order.models import Order, OrderItem
import uuid
from django.core.exceptions import PermissionDenied

from django.utils.timezone import now

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
            cart = Cart.objects.filter(customer=customer).first()
            if not cart:
                return Response({"error": "No active cart found for the user."}, status=status.HTTP_404_NOT_FOUND)

            # Calculate the total amount for the cart
            total = cart.calculate_total()
            if total <= 0:
                return Response({"error": "Cart total must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)

            # Generate a unique order ID
            unique_order_id = f"ORDER-{now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"

            # Initialize Razorpay client and create a Razorpay order
            razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
            razorpay_order = razorpay_client.order.create({
                "amount": int(total * 100),
                "currency": "INR",
                "payment_capture": "1"
            })

            # Create RazorpayOrder with the correct fields
            razorpay_order_obj = RazorpayOrder.objects.create(
                cart=cart,
                order_id=razorpay_order['id'],
                unique_order_id=unique_order_id
            )

            # Get the vendor from the first cart item
            first_cart_item = cart.items.first()
            vendor = first_cart_item.product.created_by

            # Create Order
            order = Order.objects.create(
                user=request.user,
                order_id=unique_order_id,
                total_price=total,
                customer_email=customer.customer_email,
                vendor_email=vendor.vendor_email,
                razorpay_order=razorpay_order_obj
            )

            # Create OrderItems for each CartItem with unique_order_id
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product_name=cart_item.variant.sku,
                    quantity=cart_item.quantity,
                    price=cart_item.get_price(),
                    unique_order_id=unique_order_id  # Add unique_order_id here
                )

            # Send email notifications
            self._send_notifications(
                customer=customer,
                vendor=vendor,
                unique_order_id=unique_order_id,
                total=total,
                store_name=vendor.store_name
            )
            

            return Response({
                "razorpay_order_id": razorpay_order['id'],
                "unique_order_id": unique_order_id,
                "total_price": total,
                "currency": "INR",
                "cart_id": cart.id
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def _send_notifications(self, customer, vendor, unique_order_id, total, store_name):
        subject = f"🎉 New Order: {unique_order_id} 🎉"

        customer_message = f"""
        🎉 **Thank You for Your Order, {customer.customer_name}!** 🎉

        We're excited to let you know that your order has been successfully placed. 🛍️

        **Order ID**: {unique_order_id}  
        **Total Price**: ₹{total}

        Thank you for choosing {store_name} — we can't wait to serve you again! 💖

        Warm regards,  
        The {store_name} Team
        """

        vendor_message = f"""
        🚨 **New Order Alert!** 🚨

        A new order has been placed! 🛒

        **Order ID**: {unique_order_id}  
        **Customer**: {customer.customer_name}  
        **Total Price**: ₹{total}  
        **Status**: Processing

        Please process this order as soon as possible and ensure timely delivery. 🚚

        Best,  
        The MultiVendor Team
        """

        # Send emails
        send_mail(subject, customer_message, settings.DEFAULT_FROM_EMAIL, [customer.customer_email])
        send_mail(subject, vendor_message, settings.DEFAULT_FROM_EMAIL, [vendor.vendor_email])


class ReorderCreateRazorpayOrderAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        """
        Reorder a previous order and create a Razorpay order for payment.
        """
        try:
            # Ensure the user is a customer
            if not hasattr(request.user, 'customer_profile'):
                raise PermissionDenied("Only customers are allowed to reorder.")

            # Fetch the original order
            original_order = Order.objects.get(order_id=order_id, user=request.user)
            items = original_order.items.all()
            if not items:
                return Response({"error": "Original order has no items."}, status=status.HTTP_404_NOT_FOUND)

            # Calculate total price
            total_price = sum(item.price * item.quantity for item in items)
            if total_price <= 0:
                return Response({"error": "Total price must be greater than zero."}, status=status.HTTP_400_BAD_REQUEST)

            # Generate unique order ID
            unique_order_id = f"REORDER-{now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"

            # Create a Razorpay order
            razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
            razorpay_order = razorpay_client.order.create({
                "amount": int(total_price * 100),
                "currency": "INR",
                "payment_capture": "1"
            })

            # Save RazorpayOrder instance
            razorpay_order_obj = RazorpayOrder.objects.create(
                cart=None,  # No cart associated for reorders
                payment_id=razorpay_order['id'],
                unique_order_id=unique_order_id
            )

            # Create the new order and copy the original details
            new_order = Order.objects.create(
                user=request.user,
                order_id=unique_order_id,
                total_price=total_price,
                customer_email=original_order.customer_email,
                vendor_email=original_order.vendor_email,
                razorpay_order=razorpay_order_obj
            )

            # Duplicate the items for the new order
            for item in items:
                OrderItem.objects.create(
                    order=new_order,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    price=item.price,
                    unique_order_id=unique_order_id
                )

            # Send notifications
            self._send_notifications(
                customer_email=new_order.customer_email,
                vendor_email=new_order.vendor_email,
                unique_order_id=unique_order_id,
                total_price=total_price,
                store_name=Vendor.objects.get(vendor_email=new_order.vendor_email).store_name
            )

            return Response({
                "razorpay_order_id": razorpay_order['id'],
                "unique_order_id": unique_order_id,
                "total_price": total_price,
                "currency": "INR"
            }, status=status.HTTP_201_CREATED)

        except Order.DoesNotExist:
            return Response({"error": "Original order not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def _send_notifications(self, customer_email, vendor_email, unique_order_id, total_price, store_name):
        subject = f"🔄 Reorder Created: {unique_order_id} 🔄"

        if customer_email:
            customer_message = f"""
            Thank you for reordering! Your new order has been placed.

            **Order ID**: {unique_order_id}  
            **Total Price**: ₹{total_price}
            """
            send_mail(subject, customer_message, settings.DEFAULT_FROM_EMAIL, [customer_email])

        if vendor_email:
            vendor_message = f"""
            A new reorder has been placed by a customer.

            **Order ID**: {unique_order_id}  
            **Total Price**: ₹{total_price}
            """
            send_mail(subject, vendor_message, settings.DEFAULT_FROM_EMAIL, [vendor_email])
