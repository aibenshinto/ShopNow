from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Review, ProductVariant, Reply,Customer,Vendor
from .serializers import ReviewSerializer, ReplySerializer
from rest_framework_simplejwt.authentication import JWTAuthentication


class ReviewAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, product_variant_id):
        """Fetch all reviews for a specific product variant."""
        reviews = Review.objects.filter(product_variant__id=product_variant_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def post(self, request, product_variant_id):
        """Create a new review for a product variant."""
        product_variant = ProductVariant.objects.filter(id=product_variant_id).first()
        if not product_variant:
            return Response({"error": "Product variant not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        data['product_variant'] = product_variant_id
        
        
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            return Response({"error": "Customer profile not found for the user."}, status=status.HTTP_400_BAD_REQUEST)
        data['customer'] = customer.id
        
        serializer = ReviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save(customer=customer, product_variant=product_variant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReplyAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, review_id):
        """Vendor replies to a review."""
        review = Review.objects.filter(id=review_id).first()
        if not review:
            return Response({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)

        # Ensure only the vendor of the product can reply
        print(review.product_variant.product.created_by.user)
        print(request.user)
        if review.product_variant.product.created_by.user != request.user:
            return Response({"error": "You are not authorized to reply to this review."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        data['review'] = review_id
        vendor = Vendor.objects.filter(user=request.user).first()
        if not vendor:
            return Response({"error": "Vendor profile not found for the user."}, status=status.HTTP_400_BAD_REQUEST)
        data['vendor'] = vendor.id
        serializer = ReplySerializer(data=data)
        if serializer.is_valid():
            serializer.save(vendor=vendor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)