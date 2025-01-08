from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem
from .serializers import OrderSerializer
from django.contrib.auth.models import User

from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem
from .serializers import OrderSerializer
from django.core.mail import send_mail
from django.conf import settings
import uuid
from .models import ORDER_STATUS_CHOICES
from rest_framework.permissions import AllowAny

class CreateOrderView(APIView):
    def post(self, request):
        # For anonymous users, user will be None
        user = request.user if request.user.is_authenticated else None

        data = request.data
        items_data = data.get('items', [])
        total_price = sum(item['price'] * item['quantity'] for item in items_data)

        # Get customer email and vendor email from request data (will use model defaults if not provided)
        customer_email = data.get('customer_email', None)  # Will fall back to model default if None
        vendor_email = data.get('vendor_email', None)  # Will fall back to model default if None

        # Create the order with emails
        order = Order.objects.create(
            user=user,
            total_price=total_price,
            customer_email=customer_email or Order._meta.get_field('customer_email').default,
            vendor_email=vendor_email or Order._meta.get_field('vendor_email').default,
        )

        # Create the order items
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        # Send notifications to customer and vendor
        self.send_order_notification(order)

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def send_order_notification(self, order):
        subject = f"New Order: {order.order_id}"
        message = f"Order {order.order_id} has been placed with a total price of {order.total_price}."

        # Send email to the customer
        if order.customer_email:
            send_mail(
                subject,
                f"Thank you for your order! Your order ID is {order.order_id}.",
                settings.DEFAULT_FROM_EMAIL,
                [order.customer_email],
            )

        # Send email to the vendor
        if order.vendor_email:
            send_mail(
                subject,
                f"New order has been placed! Order ID: {order.order_id}, Total: {order.total_price}",
                settings.DEFAULT_FROM_EMAIL,
                [order.vendor_email],
            )


class OrderDetailView(APIView):
    def get(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        


class OrderHistoryView(APIView):
    
    def get(self, request):
        """
        Retrieve all order history for unauthenticated users or filter by user if authenticated.
        """
        if request.user.is_authenticated:
            # Retrieve orders specific to the logged-in user
            orders = Order.objects.filter(user=request.user).order_by('-created_at')
        else:
            # For unauthenticated users, retrieve all orders
            orders = Order.objects.all().order_by('-created_at')

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Re-order functionality: Create a new order based on a previous one.
        Only authenticated users are allowed to use this functionality.
        """
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        order_id = request.data.get('order_id')
        try:
            # Find the original order
            order = Order.objects.get(order_id=order_id, user=request.user)
            items = order.items.all()

            # Calculate total price for the new order
            total_price = sum(item.price * item.quantity for item in items)

            # Create a new order
            new_order = Order.objects.create(
                user=request.user,
                total_price=total_price,
                customer_email=order.customer_email,
                vendor_email=order.vendor_email,
            )

            # Duplicate the items in the new order
            for item in items:
                OrderItem.objects.create(
                    order=new_order,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    price=item.price,
                )

            # Send notifications if required
            self.send_reorder_notification(new_order)

            return Response(
                {"message": "Order re-placed successfully", "order_id": new_order.order_id},
                status=status.HTTP_201_CREATED,
            )
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    def send_reorder_notification(self, order):
        subject = f"Re-Order: {order.order_id}"
        message = (
            f"Thank you for reordering! Your new order ID is {order.order_id}."
            f" Total price is {order.total_price}."
        )

        # Send email to the customer
        if order.customer_email:
            send_mail(
                subject,
                f"Your re-order has been placed successfully. Order ID: {order.order_id}.",
                settings.DEFAULT_FROM_EMAIL,
                [order.customer_email],
            )

        # Notify vendor
        if order.vendor_email:
            send_mail(
                subject,
                f"Customer reordered items. New Order ID: {order.order_id}, Total: {order.total_price}",
                settings.DEFAULT_FROM_EMAIL,
                [order.vendor_email],
            )

class UpdateOrderStatusView(APIView):
    def patch(self, request, order_id):
        try:
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
                        [order.customer_email],  # Ensure the correct recipient is the customer's email
                    )

                # Notify the vendor about the status update
                if order.vendor_email:
                    send_mail(
                        f"Order {order.order_id} Status Update",
                        f"The order status has been updated to '{order.status}'.",
                        settings.DEFAULT_FROM_EMAIL,
                        [order.vendor_email],  # Ensure the vendor gets this email
                    )

                return Response({"message": "Order status updated successfully."}, status=status.HTTP_200_OK)

            return Response({"error": "Invalid status provided."}, status=status.HTTP_400_BAD_REQUEST)

        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)



class ReorderView(APIView):
    permission_classes = [AllowAny]  # Allow any user to access this view
    
    def post(self, request, order_id):
        """
        Create a new order based on a previous order.
        Open to all users, no authentication required.
        """
        try:
            # Find the original order without user filter
            original_order = Order.objects.get(order_id=order_id)
            items = original_order.items.all()

            # Calculate total price for the new order
            total_price = sum(item.price * item.quantity for item in items)

            # Create a new order
            new_order = Order.objects.create(
                user=None,  # No user association
                total_price=total_price,
                customer_email=original_order.customer_email,
                vendor_email=original_order.vendor_email,
            )

            # Duplicate the items in the new order
            for item in items:
                OrderItem.objects.create(
                    order=new_order,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    price=item.price,
                )

            # Send notifications
            self._send_reorder_notification(new_order)

            serializer = OrderSerializer(new_order)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

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

        # Notify vendor
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