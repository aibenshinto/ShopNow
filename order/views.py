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

# class CreateOrderView(APIView):
    
#     def post(self, request):
#         # For anonymous users, user will be None
#         user = request.user if request.user.is_authenticated else None

#         data = request.data
#         items_data = data.get('items', [])
#         total_price = sum(item['price'] * item['quantity'] for item in items_data)

#         # Get customer email and vendor email from request data (will use model defaults if not provided)
#         customer_email = data.get('customer_email', None)  # Will fall back to model default if None
#         vendor_email = data.get('vendor_email', None)  # Will fall back to model default if None

#         # Create the order with emails
#         order = Order.objects.create(
#             user=user,
#             total_price=total_price,
#             customer_email=customer_email or Order._meta.get_field('customer_email').default,
#             vendor_email=vendor_email or Order._meta.get_field('vendor_email').default,
#         )

#         # Create the order items
#         for item_data in items_data:
#             OrderItem.objects.create(order=order, **item_data)

#         # Send notifications to customer and vendor
#         self.send_order_notification(order)

#         serializer = OrderSerializer(order)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


#     def send_order_notification(self, order):
#         subject = f"New Order: {order.order_id}"
#         message = f"Order {order.order_id} has been placed with a total price of {order.total_price}."

#         # Send email to the customer
#         if order.customer_email:
#             send_mail(
#                 subject,
#                 f"Thank you for your order! Your order ID is {order.order_id}.",
#                 settings.DEFAULT_FROM_EMAIL,
#                 [order.customer_email],
#             )

#         # Send email to the vendor
#         if order.vendor_email:
#             send_mail(
#                 subject,
#                 f"New order has been placed! Order ID: {order.order_id}, Total: {order.total_price}",
#                 settings.DEFAULT_FROM_EMAIL,
#                 [order.vendor_email],
#             )



class CreateOrderView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Ensure the authenticated user is a customer
        if not hasattr(request.user, 'customer_profile'):
            return Response(
                {"error": "Access denied. Only customers can place orders."},
                status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data
        items_data = data.get('items', [])

        if not items_data:
            return Response({"error": "No items provided for the order."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch customer email from the customer profile
        try:
            customer_email = request.user.customer_profile.customer_email
        except AttributeError:
            return Response({"error": "Customer email is not available."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate the total price
        total_price = sum(item['price'] * item['quantity'] for item in items_data)

        # Create the order associated with the authenticated customer
        order = Order.objects.create(
            user=request.user,  # Associate the order with the customer
            total_price=total_price,
            customer_email=customer_email,  # Fetch the customer's email from their profile
            vendor_email=data.get('vendor_email', None),  # Optional: provided by the request
        )

        # Create the order items
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        # Send notifications to the customer and vendor
        try:
            self.send_order_notification(order)
        except Exception as e:
            logging.error(f"Failed to send email notifications: {str(e)}")

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def send_order_notification(self, order):
        subject = f"🎉 New Order: {order.order_id} 🎉"
        
        customer_message = f"""
        🎉 **Thank You for Your Order, {order.user}!** 🎉

        We’re excited to let you know that your order has been successfully placed. 🛍️

        **Order ID**: {order.order_id}  
        **Total Price**: ${order.total_price}

        You’ll receive an update once your order is on its way! 🚚

        Thank you for choosing us — we can’t wait to serve you again! 💖

        If you have any questions, feel free to reach out to us anytime.

        Warm regards,  
        The [Your Store Name] Team
        """
        vendor_message = f"""
        🚨 **New Order Alert!** 🚨

        A new order has been placed! 🛒

        **Order ID**: {order.order_id}  
        **Customer**: {order.user}  
        **Total Price**: ${order.total_price}  
        **Status**: Processing

        Please process this order as soon as possible and ensure timely delivery. 🚚

        Thanks for your great work in making our customers happy!

        Best,  
        The MultiVendor Team
        """

        # Notify the customer
        try:
            if order.customer_email:
                send_mail(
                    subject,
                    customer_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [order.customer_email],
                )
                print(f"Customer email sent to: {order.customer_email}")
        except Exception as e:
            logging.error(f"Failed to send email to customer ({order.customer_email}): {str(e)}")

        # Notify the vendor
        try:
            if order.vendor_email:
                send_mail(
                    subject,
                    vendor_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [order.vendor_email],
                )
                print(f"Vendor email sent to: {order.vendor_email}")
        except Exception as e:
            logging.error(f"Failed to send email to vendor ({order.vendor_email}): {str(e)}")





class OrderDetailView(APIView):
    def get(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        


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

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# class UpdateOrderStatusView(APIView):
#     def patch(self, request, order_id):
#         try:
#             order = Order.objects.get(order_id=order_id)
#             new_status = request.data.get('status', None)

#             if new_status and new_status in dict(ORDER_STATUS_CHOICES):
#                 order.status = new_status
#                 order.save()

#                 # Notify the customer about the status update
#                 if order.customer_email:
#                     send_mail(
#                         f"Order {order.order_id} Status Update",
#                         f"Your order status has been updated to '{order.status}'.",
#                         settings.DEFAULT_FROM_EMAIL,
#                         [order.customer_email],  # Ensure the correct recipient is the customer's email
#                     )

#                 # Notify the vendor about the status update
#                 if order.vendor_email:
#                     send_mail(
#                         f"Order {order.order_id} Status Update",
#                         f"The order status has been updated to '{order.status}'.",
#                         settings.DEFAULT_FROM_EMAIL,
#                         [order.vendor_email],  # Ensure the vendor gets this email
#                     )

#                 return Response({"message": "Order status updated successfully."}, status=status.HTTP_200_OK)

#             return Response({"error": "Invalid status provided."}, status=status.HTTP_400_BAD_REQUEST)

#         except Order.DoesNotExist:
#             return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
class UpdateOrderStatusView(APIView):
    authentication_classes = [JWTAuthentication]  # Specify JWTAuthentication here
    permission_classes = [IsAuthenticated]
    def patch(self, request, order_id):
        try:
            # Check if the logged-in user is a vendor or customer
            if hasattr(request.user, 'vendor_profile'):
                # Vendor logic
                order = Order.objects.get(order_id=order_id)
                new_status = request.data.get('status', None)

                if new_status and new_status in dict(ORDER_STATUS_CHOICES):
                    order.status = new_status
                    order.save()

                    # Notify the customer about the status update
                    if order.customer_email:
                        send_mail(
                            f"Order {order.order_id} Status Update",
                            f"Your order status has been updated to '{order.status}'.",
                            settings.DEFAULT_FROM_EMAIL,
                            [order.customer_email],
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

        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)



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
        subject = f"Re-Order: {order.order_id}"
        
        # Send email to the customer
        if order.customer_email:
            customer_message = (
                f"Your re-order has been placed successfully.\n"
                f"Order ID: {order.order_id}\n"
                f"Total: ${order.total_price}"
            )
            send_mail(
                subject,
                customer_message,
                settings.DEFAULT_FROM_EMAIL,
                [order.customer_email],
            )

        # Notify the vendor
        if order.vendor_email:
            vendor_message = (
                f"Customer reordered items.\n"
                f"New Order ID: {order.order_id}\n"
                f"Total: ${order.total_price}"
            )
            send_mail(
                subject,
                vendor_message,
                settings.DEFAULT_FROM_EMAIL,
                [order.vendor_email],
            )


class VendorDashboardView(APIView):
    def get(self, request):
        """
        View the vendor dashboard with all orders, sales, earnings, and admin commission.
        """
        # Retrieve all orders for the vendor (using the vendor email in the Order model)
        orders = Order.objects.filter(vendor_email='farizz1132pulikkal@gmail.com')  # Single vendor email
        total_sales = orders.aggregate(total_sales=Sum('total_price'))['total_sales'] or 0
        earnings = self.calculate_earnings(total_sales)
        admin_commission = self.calculate_admin_commission(total_sales)

        # Format the data for the dashboard
        dashboard_data = {
            "total_orders": orders.count(),
            "total_sales": total_sales,
            "earnings": earnings,
            "admin_commission": admin_commission,  # Admin's commission on the sales
            "orders": OrderSerializer(orders, many=True).data,
        }

        return Response(dashboard_data, status=status.HTTP_200_OK)

    def calculate_earnings(self, total_sales):
        """
        Calculates vendor earnings based on a commission (for example, 90% of total sales).
        """
        commission_rate = Decimal(0.10)  # 10% commission rate for admin
        earnings = total_sales * (Decimal(1) - commission_rate)  # Vendor earns 90% of the total sales
        return earnings

    def calculate_admin_commission(self, total_sales):
        """
        Calculates admin's commission (for example, 10% of total sales).
        """
        commission_rate = Decimal(0.10)  # 10% commission for admin
        admin_commission = total_sales * commission_rate
        return admin_commission