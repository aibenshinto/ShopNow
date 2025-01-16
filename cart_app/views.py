from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from product_app.models import Product, ProductVariant
from authentication_app.models import Customer
from shippinaddress.models import AddressBook
from rest_framework_simplejwt.authentication import JWTAuthentication




class AddToCartView(APIView):
    """
    View to add items to the cart. Requires authentication.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            # Ensure we retrieve the Customer instance
            try:
                customer = Customer.objects.get(user=request.user)
            except Customer.DoesNotExist:
                return Response({"error": "Customer not found."}, status=status.HTTP_400_BAD_REQUEST)

            product_id = data.get("product")
            variant_id = data.get("variant", None)
            quantity = data.get("quantity", 1)

            # Validate product and variant
            product = get_object_or_404(Product, id=product_id)
            variant = ProductVariant.objects.filter(id=variant_id).first() if variant_id else None

            # Get or create the cart for the authenticated customer
            cart, created = Cart.objects.get_or_create(customer=customer)

            # Validate stock
            if variant:
                if variant.stock < quantity:
                    return Response({"error": "Insufficient stock for variant."}, status=status.HTTP_400_BAD_REQUEST)
            elif product.stock < quantity:
                return Response({"error": "Insufficient stock for product."}, status=status.HTTP_400_BAD_REQUEST)

            # Add or update item in the cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                variant=variant,
                defaults={"quantity": quantity},
            )

            if not created:
                cart_item.quantity += quantity
                if cart_item.quantity > (variant.stock if variant else product.stock):
                    return Response({"error": "Exceeds available stock."}, status=status.HTTP_400_BAD_REQUEST)
                cart_item.save()

            return Response({
                "message": "Product added to cart.",
                "cart_item": {
                    "id": cart_item.id,
                    "product": cart_item.product.name,
                    "variant": cart_item.variant.sku if cart_item.variant else None,
                    "quantity": cart_item.quantity
                }
            })

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class CheckoutView(APIView):
    """
    View to handle checkout for a cart. Requires authentication.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            customer = request.user
            address_id = data.get("address_id")

            # Get the cart for the authenticated user
            cart = get_object_or_404(Cart, customer=customer)

            # Validate the address
            address = get_object_or_404(AddressBook, id=address_id, customer=customer)

            # Calculate total price and validate stock
            total_price = 0
            for item in cart.items.all():
                if not item.is_in_stock():
                    return Response({
                        "error": f"Insufficient stock for {item.product.name}."
                    }, status=status.HTTP_400_BAD_REQUEST)

                price = item.get_price()
                total_price += price * item.quantity

                # Deduct stock
                if item.variant:
                    item.variant.stock -= item.quantity
                    item.variant.save()
                else:
                    item.product.stock -= item.quantity
                    item.product.save()

            # Clear the cart after checkout
            cart.items.all().delete()

            return Response({
                "message": "Checkout successful.",
                "total_price": total_price,
                "address": {
                    "address_line1": address.address_line1,
                    "address_line2": address.address_line2,
                    "city": address.city,
                    "state": address.state,
                    "postal_code": address.postal_code,
                    "country": address.country,
                    "phone_number": address.phone_number,
                },
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ViewCartView(APIView):
    """
    View to display the cart items for an authenticated user.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Ensure we retrieve the Customer instance
            try:
                customer = Customer.objects.get(user=request.user)
            except Customer.DoesNotExist:
                return Response({"error": "Customer not found."}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve the cart for the authenticated customer
            cart = get_object_or_404(Cart, customer=customer)

            # Fetch all cart items
            cart_items = cart.items.all()
            items = []
            total_price = 0  # Initialize total price

            for item in cart_items:
                # Calculate total price for the current item
                item_total_price = item.get_price() * item.quantity
                items.append({
                    "product": item.product.name,
                    "variant": item.variant.sku if item.variant else None,
                    "quantity": item.quantity,
                    "unit_price": item.get_price(),
                    "total_price": item_total_price,
                })
                total_price += item_total_price  # Accumulate the total price

            return Response({
                "cart_items": items,
                "total_price": total_price
            })
        except Exception as e:
            # Handle and log errors
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DeleteFromCartView(APIView):
    """
    View to delete a cart item. Requires authentication.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data

            # Ensure we retrieve the Customer instance
            try:
                customer = Customer.objects.get(user=request.user)
            except Customer.DoesNotExist:
                return Response({"error": "Customer not found."}, status=status.HTTP_400_BAD_REQUEST)

            product_id = data.get("product")
            variant_id = data.get("variant", None)

            # Retrieve the cart for the authenticated customer
            cart = get_object_or_404(Cart, customer=customer)

            # Retrieve the cart item based on the product and optional variant
            if variant_id:
                cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id, variant_id=variant_id)
            else:
                cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id, variant_id__isnull=True)

            # Delete the cart item
            cart_item.delete()

            return Response({"message": "Item successfully deleted from cart."})

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

