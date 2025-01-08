from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ProductSerializer

class ProductCreateView(APIView):
    
    def post(self, request, *args, **kwargs):
        serializer = ProductSerializer(data=request.data)

        # Validate the request data
        if serializer.is_valid():
            # Create the product and related data (attributes, variants)
            product = serializer.save()

            return Response({
                'message': 'Product created successfully',
                'product': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
