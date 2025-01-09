from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from .models import Cart, CartItem
from product_app.models import Product, ProductVariant  # Importing models from product_app
from django.contrib.auth.models import User

@method_decorator(csrf_exempt, name='dispatch')
def add_to_cart(request):
    """
    View to add items to the cart.
    Handles both guest users (session_id) and authenticated users (user_id).
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            session_id = data.get("session_id", None)
            user_id = data.get("user", None)
            product_id = data.get("product")
            variant_id = data.get("variant", None)
            quantity = data.get("quantity", 1)

            # Validate product and variant
            product = get_object_or_404(Product, id=product_id)
            variant = ProductVariant.objects.filter(id=variant_id).first() if variant_id else None

            # Get or create the cart for the user or session
            if user_id:
                user = get_object_or_404(User, id=user_id)
                cart, created = Cart.objects.get_or_create(user=user)
            elif session_id:
                cart, created = Cart.objects.get_or_create(session_id=session_id)
            else:
                return JsonResponse({"error": "User or session ID is required."}, status=400)

            # Validate stock before adding item to cart
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

            return JsonResponse({
                "message": "Product added to cart.",
                "cart_item": {
                    "id": cart_item.id,
                    "product": cart_item.product.name,
                    "variant": cart_item.variant.sku if cart_item.variant else None,
                    "quantity": cart_item.quantity
                }
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)


@method_decorator(csrf_exempt, name='dispatch')
def checkout(request):
    """
    View to handle checkout for a cart.
    Clears the cart after successfully processing the checkout.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            session_id = data.get("session_id", None)
            user_id = data.get("user", None)

            # Get the cart for the user or session
            if user_id:
                user = get_object_or_404(User, id=user_id)
                cart = get_object_or_404(Cart, user=user)
            elif session_id:
                cart = get_object_or_404(Cart, session_id=session_id)
            else:
                return JsonResponse({"error": "User or session ID is required."}, status=400)

            # Calculate total price and validate stock
            total_price = 0
            for item in cart.items.all():
                # Check stock before checkout
                if not item.is_in_stock():
                    return JsonResponse({
                        "error": f"Insufficient stock for {item.product.name}."
                    }, status=400)

                # Get price and calculate total price
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
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)


@method_decorator(csrf_exempt, name='dispatch')
def view_cart(request, user_id=None, session_id=None):
    """
    View to display the contents of a cart.
    """
    if request.method == "GET":
        try:
            # Get the cart for the user or session
            if user_id:
                user = get_object_or_404(User, id=user_id)
                cart = get_object_or_404(Cart, user=user)
            elif session_id:
                cart = get_object_or_404(Cart, session_id=session_id)
            else:
                return JsonResponse({"error": "User or session ID is required."}, status=400)

            cart_items = cart.items.all()
            items = [
                {
                    "product": item.product.name,
                    "variant": item.variant.sku if item.variant else None,
                    "quantity": item.quantity,
                    "price": item.get_price(),  # Use the get_price method for the price
                }
                for item in cart_items
            ]

            return JsonResponse({"cart_items": items})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)
