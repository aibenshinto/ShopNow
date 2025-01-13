from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from .models import Cart, CartItem
from product_app.models import Product, ProductVariant
from authentication_app.models import Customer  # Importing the Customer model
from shippinaddress.models import AddressBook
import uuid

@method_decorator(csrf_exempt, name='dispatch')
def add_to_cart(request):
    """
    View to add items to the cart.
    Handles both guest users (session_id) and authenticated users (customer_id).
    """
    if request.method == "POST":
        try:
            # Parse the request body
            data = json.loads(request.body)

            session_id = data.get("session_id", None)
            customer_id = data.get("customer", None)
            product_id = data.get("product")
            variant_id = data.get("variant", None)
            quantity = data.get("quantity", 1)

            # Validate product and variant
            product = get_object_or_404(Product, id=product_id)
            variant = ProductVariant.objects.filter(id=variant_id).first() if variant_id else None

            # Handle guest or authenticated user cart
            if customer_id:
                customer = get_object_or_404(Customer, id=customer_id)
                cart, created = Cart.objects.get_or_create(customer=customer)
            else:
                if not session_id:
                    session_id = str(uuid.uuid4())  # Create a new session ID if not provided
                cart, created = Cart.objects.get_or_create(session_id=session_id)

            # Validate stock
            if variant:
                if variant.stock < quantity:
                    return JsonResponse({"error": "Insufficient stock for variant."}, status=400)
            elif product.stock < quantity:
                return JsonResponse({"error": "Insufficient stock for product."}, status=400)

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
                    return JsonResponse({"error": "Exceeds available stock."}, status=400)
                cart_item.save()

            response = JsonResponse({
                "message": "Product added to cart.",
                "cart_item": {
                    "id": cart_item.id,
                    "product": cart_item.product.name,
                    "variant": cart_item.variant.sku if cart_item.variant else None,
                    "quantity": cart_item.quantity
                },
                "session_id": session_id  # Include session ID for guest users
            })
            response.set_cookie('session_id', session_id, max_age=60*60*24*30, httponly=True)

            return response

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)

@method_decorator(csrf_exempt, name='dispatch')
def checkout(request):
    """
    View to handle checkout for a cart.
    Includes the user's address ID in the request body.
    Clears the cart after successfully processing the checkout.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            session_id = data.get("session_id", None)
            customer_id = data.get("customer", None)
            address_id = data.get("address_id", None)

            # Get the cart for the customer or session
            if customer_id:
                customer = get_object_or_404(Customer, id=customer_id)
                cart = get_object_or_404(Cart, customer=customer)
            elif session_id:
                cart = get_object_or_404(Cart, session_id=session_id)
            else:
                return JsonResponse({"error": "Customer or session ID is required."}, status=400)

            # Validate the address
            if address_id:
                address = get_object_or_404(AddressBook, id=address_id, customer=customer)
            else:
                return JsonResponse({"error": "Address ID is required."}, status=400)

            # Calculate total price and validate stock
            total_price = 0
            for item in cart.items.all():
                if not item.is_in_stock():
                    return JsonResponse({
                        "error": f"Insufficient stock for {item.product.name}."
                    }, status=400)

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

            return JsonResponse({
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
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)

@method_decorator(csrf_exempt, name='dispatch')
def view_cart(request, customer_id=None, session_id=None):
    if request.method == "GET":
        try:
            if customer_id:
                customer = get_object_or_404(Customer, id=customer_id)
                cart = get_object_or_404(Cart, customer=customer)
            elif session_id:
                cart = get_object_or_404(Cart, session_id=session_id)
            else:
                return JsonResponse({"error": "Customer or session ID is required."}, status=400)

            cart_items = cart.items.all()
            items = [
                {
                    "product": item.product.name,
                    "variant": item.variant.sku if item.variant else None,
                    "quantity": item.quantity,
                    "price": item.get_price(),
                }
                for item in cart_items
            ]
            return JsonResponse({"cart_items": items})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)


@method_decorator(csrf_exempt, name='dispatch')
def delete_from_cart(request):
    """
    View to delete a cart item.
    Handles both guest users (session_id) and authenticated users (customer_id).
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            session_id = data.get("session_id", None)
            customer_id = data.get("customer", None)
            product_id = data.get("product")
            variant_id = data.get("variant", None)

            if not (product_id and (customer_id or session_id)):
                return JsonResponse({"error": "Product ID and either customer ID or session ID are required."}, status=400)

            if customer_id:
                customer = get_object_or_404(Customer, id=customer_id)
                cart = get_object_or_404(Cart, customer=customer)
            elif session_id:
                cart = get_object_or_404(Cart, session_id=session_id)
            else:
                return JsonResponse({"error": "Customer or session ID is required."}, status=400)

            if variant_id:
                cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id, variant_id=variant_id)
            else:
                cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id, variant_id__isnull=True)

            cart_item.delete()

            return JsonResponse({"message": "Item successfully deleted from cart."})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)
