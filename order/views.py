from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
import logging
from .models import Order, OrderItem
from .serializers import OrderSerializer
from django.core.mail import send_mail
from django.conf import settings
import uuid
from decimal import Decimal
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import ORDER_STATUS_CHOICES
from rest_framework.permissions import AllowAny
from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import PermissionDenied
from authentication_app.models import Vendor

# class CreateOrderView(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         # Ensure the authenticated user is a customer
#         if not hasattr(request.user, 'customer_profile'):
#             return Response(
#                 {"error": "Access denied. Only customers can place orders."},
#                 status=status.HTTP_403_FORBIDDEN,
#             )

#         data = request.data
#         items_data = data.get('items', [])

#         if not items_data:
#             return Response({"error": "No items provided for the order."}, status=status.HTTP_400_BAD_REQUEST)

#         # Fetch customer email from the customer profile
#         try:
#             customer_email = request.user.customer_profile.customer_email
#         except AttributeError:
#             return Response({"error": "Customer email is not available."}, status=status.HTTP_400_BAD_REQUEST)

#         # Calculate the total price
#         total_price = sum(item['price'] * item['quantity'] for item in items_data)

#         # Create the order associated with the authenticated customer
#         order = Order.objects.create(
#             user=request.user,  # Associate the order with the customer
#             total_price=total_price,
#             customer_email=customer_email,  # Fetch the customer's email from their profile
#             vendor_email=data.get('vendor_email', None),  # Optional: provided by the request
#         )

#         # Create the order items
#         for item_data in items_data:
#             OrderItem.objects.create(order=order, **item_data)

#         # Send notifications to the customer and vendor
#         try:
#             self.send_order_notification(order)
#         except Exception as e:
#             logging.error(f"Failed to send email notifications: {str(e)}")

#         serializer = OrderSerializer(order)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     def send_order_notification(self, order):
#         vendor = Vendor.objects.get(vendor_email=order.vendor_email)
#         store_name = vendor.store_name
#         subject = f"🎉 New Order: {order.order_id} 🎉"
        
#         customer_message = f"""
#         🎉 **Thank You for Your Order, {order.user}!** 🎉

#         We’re excited to let you know that your order has been successfully placed. 🛍️

#         **Order ID**: {order.order_id}  
#         **Total Price**: ${order.total_price}

#         You’ll receive an update once your order is on its way! 🚚

#         Thank you for choosing {store_name} — we can’t wait to serve you again! 💖

#         If you have any questions, feel free to reach out to us anytime.

#         Warm regards,  
#         The {store_name} Team
#         """
#         vendor_message = f"""
#         🚨 **New Order Alert!** 🚨

#         A new order has been placed! 🛒

#         **Order ID**: {order.order_id}  
#         **Customer**: {order.user}  
#         **Total Price**: ${order.total_price}  
#         **Status**: Processing

#         Please process this order as soon as possible and ensure timely delivery. 🚚

#         Thanks for your great work in making our customers happy!

#         Best,  
#         The MultiVendor Team
#         """

#         # Notify the customer
#         try:
#             if order.customer_email:
#                 send_mail(
#                     subject,
#                     customer_message,
#                     settings.DEFAULT_FROM_EMAIL,
#                     [order.customer_email],
#                 )
#                 print(f"Customer email sent to: {order.customer_email}")
#         except Exception as e:
#             logging.error(f"Failed to send email to customer ({order.customer_email}): {str(e)}")

#         # Notify the vendor
#         try:
#             if order.vendor_email:
#                 send_mail(
#                     subject,
#                     vendor_message,
#                     settings.DEFAULT_FROM_EMAIL,
#                     [order.vendor_email],
#                 )
#                 print(f"Vendor email sent to: {order.vendor_email}")
#         except Exception as e:
#             logging.error(f"Failed to send email to vendor ({order.vendor_email}): {str(e)}")





class OrderDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            # Fetch the order and its related data
            order = Order.objects.prefetch_related('items', 'razorpay_order').get(order_id=order_id)

            # Check if the logged-in user is either the customer or the vendor for this order
            if (
                request.user != order.user and
                not (hasattr(request.user, 'vendor_profile') and
                     request.user.vendor_profile.vendor_email == order.vendor_email)
            ):
                raise PermissionDenied("Access denied. You are not authorized to view this order.")

            # Serialize the order
            serializer = OrderSerializer(order)
            order_data = serializer.data

            # Remove `unique_order_id` from order items
            for item in order_data['items']:
                if 'unique_order_id' in item:
                    del item['unique_order_id']

            # Remove `unique_order_id` from payment_info (razorpay details)
            if 'unique_order_id' in order_data['razorpay_details']:
                del order_data['razorpay_details']['unique_order_id']

            response_data = {
                "payment_status": "success",
                "order_details": {
                    "basic_info": {
                        "order_id": order_data['order_id'],
                        "status": order_data['status'],
                        "total_price": order_data['total_price'],
                        "created_at": order_data['created_at'],
                        "last_updated": order_data['updated_at']
                    },
                    "customer_info": {
                        "email": order_data['customer_email']
                    },
                    "vendor_info": {
                        "email": order_data['vendor_email']
                    },
                    "payment_info": order_data['razorpay_details'],
                    "order_items": order_data['items']
                }
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({"status": "error", "message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.permissions import IsAuthenticated

class OrderHistoryView(APIView):
    authentication_classes = [JWTAuthentication]  # Specify JWTAuthentication for user verification
    permission_classes = [IsAuthenticated]  # Only authenticated users are allowed

    def get(self, request):
        """
        Retrieve the order history of the authenticated user.
        """
        # Retrieve orders specific to the logged-in user
        orders = Order.objects.filter(user=request.user).order_by('-created_at')

        # Serialize the order data
        serializer = OrderSerializer(orders, many=True)
        order_data = serializer.data

        # Remove `unique_order_id` from the required fields
        for order in order_data:
            # Remove `unique_order_id` from the razorpay details if present
            if 'razorpay_details' in order and order['razorpay_details'] is not None and 'unique_order_id' in order['razorpay_details']:
                del order['razorpay_details']['unique_order_id']
            
            # Remove `unique_order_id` from individual products in the `items` list
            if 'items' in order:
                for item in order['items']:
                    if 'unique_order_id' in item:
                        del item['unique_order_id']

        return Response(order_data, status=status.HTTP_200_OK)


class UpdateOrderStatusView(APIView):
    authentication_classes = [JWTAuthentication]  # Specify JWTAuthentication here
    permission_classes = [IsAuthenticated]

    def patch(self, request, order_id):
        
        try:
            vendor_email = request.user.email  # Get the logged-in vendor's email
            order = Order.objects.get(order_id=order_id)

            # Log vendor email details for debugging
            # print(f"Request User: {request.user}")  # Ensure this prints the user object
            # print(f"Email from Request User: {request.user.vendor_profile.vendor_email}")  # Check if email exists

            print(f"Order's Vendor Email: {order.vendor_email}")    
            # Check if the logged-in user is a vendor
            if hasattr(request.user, 'vendor_profile'):
                vendor_profile = request.user.vendor_profile
                store_name = vendor_profile.store_name  # Fetch the store name
                vendor_email = request.user.email  # Get the logged-in vendor's email

                # Fetch the order
                try:
                    order = Order.objects.get(order_id=order_id)
                except Order.DoesNotExist:
                    return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

                # Verify if the logged-in vendor is authorized to update this order
                if order.vendor_email != request.user.vendor_profile.vendor_email:
                    return Response(
                        {"error": "Access denied. You are not authorized to update this order."},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                # Update the order status
                new_status = request.data.get('status', None)
                if new_status and new_status in dict(ORDER_STATUS_CHOICES):
                    order.status = new_status
                    order.save()

                    # Notify the customer about the status update
                    if order.customer_email:
                        customer_message = f"""
                            🔔 **Order Status Update for {order.user}!** 🔔

                            Hello {order.user},  

                            We hope this message finds you well! We're writing to keep you updated about the latest status of your order. 🎉  

                            **Order Details:**  
                            - **Order ID**: {order.order_id}  
                            - **Total Price**: ${order.total_price}  
                            - **Updated Status**: {order.status}  

                            📦 Our team is working diligently to ensure everything is perfect for your order. We’ll notify you as soon as it progresses further!

                            💡 Need Assistance?  
                            If you have any questions, concerns, or just want to say hello, our support team is here for you anytime. Simply reach out, and we’ll be happy to assist you.  

                            Thank you for choosing {store_name}. Your trust and loyalty inspire us every day. 🌟  

                            Warm regards,  
                            The {store_name} Team  
                        """

                        # Send an email
                        send_mail(
                            subject=f"Order Status Update - {order.order_id}",
                            message=customer_message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[order.customer_email],
                        )

                    return Response({"message": "Order status updated successfully."}, status=status.HTTP_200_OK)

                return Response({"error": "Invalid status provided."}, status=status.HTTP_400_BAD_REQUEST)

            elif hasattr(request.user, 'customer_profile'):
                # Customer cannot update order status
                return Response(
                    {"error": "Access denied. Customers cannot update order status."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            else:
                # User is neither a vendor nor a customer
                return Response(
                    {"error": "Access denied. User is not authorized."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class ReorderView(APIView):
    authentication_classes = [JWTAuthentication]  # Specify JWTAuthentication here
    permission_classes = [IsAuthenticated]  # Only authenticated users are allowed

    def post(self, request, order_id):
        """
        Create a new order based on a previous one.
        Only customers can access this view.
        """
        try:
            # Ensure the user is a customer
            if not hasattr(request.user, 'customer_profile'):
                raise PermissionDenied("Only customers are allowed to reorder.")

            # Find the original order for this customer
            original_order = Order.objects.get(order_id=order_id, user=request.user)
            items = original_order.items.all()

            # Calculate total price for the new order
            total_price = sum(item.price * item.quantity for item in items)

            # Create a new order for the customer
            new_order = Order.objects.create(
                user=request.user,
                total_price=total_price,
                customer_email=original_order.customer_email,
                vendor_email=original_order.vendor_email,
            )

            # Duplicate the items for the new order
            for item in items:
                OrderItem.objects.create(
                    order=new_order,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    price=item.price,
                )

            # Notify the user of the reorder
            self._send_reorder_notification(new_order)

            serializer = OrderSerializer(new_order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    def _send_reorder_notification(self, order):
        subject = f"🔄 Re-Order Confirmation: {order.order_id} 🔄"
        vendor = Vendor.objects.get(vendor_email=order.vendor_email)
        store_name = vendor.store_name
        # Send email to the customer
        if order.customer_email:
            customer_message = f"""
            🔄 **Thank You for Reordering, {order.user}!** 🔄

            We’re thrilled to see you back! Your re-order has been successfully placed. 🛍️

            **Order ID**: {order.order_id}  
            **Total Price**: ${order.total_price}

            Rest assured, we’re already preparing your order, and you’ll receive an update once it’s on its way! 🚚

            Your continued trust means the world to us, and we look forward to serving you again. 💖

            If you have any questions, our team is here for you anytime.

            Warm regards,  
            The {store_name} Team
            """
            send_mail(
                subject,
                customer_message,
                settings.DEFAULT_FROM_EMAIL,
                [order.customer_email],
            )

        # Notify the vendor
        if order.vendor_email:
            vendor_message = f"""
            🔔 **Re-Order Alert!** 🔔

            Great news! A customer has placed a reorder. 🛒

            **Order ID**: {order.order_id}  
            **Customer**: {order.user}  
            **Total Price**: ${order.total_price}  
            **Status**: Processing

            Please prioritize this re-order for timely preparation and delivery. 🚚

            Thanks for your dedication and exceptional service!

            Best regards,  
            The MultiVendor Team
            """
            send_mail(
                subject,
                vendor_message,
                settings.DEFAULT_FROM_EMAIL,
                [order.vendor_email],
            )


