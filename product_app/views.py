from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Vendor, Category, Product, Attribute, AttributeValue, ProductVariant, ProductVariantAttribute
from .serializers import  ProductSerializer, AttributeSerializer, AttributeValueSerializer, ProductVariantSerializer, ProductVariantAttributeSerializer

# Product API
class ProductAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.is_authenticated:
            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Attribute API  
class AttributeAPIView(APIView):
    def get(self,request):
        attribute = Attribute.objects.all()
        serializer = AttributeSerializer(attribute, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        if request.user.is_authenticated:
            serializer = AttributeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Attribute Value API  
class AttributeValueAPIView(APIView):
    def get(self,request):
        attributevalue = AttributeValue.objects.all()
        serializer = AttributeValueSerializer(attributevalue, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        if request.user.is_authenticated:
            serializer = AttributeValueSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Product Variant API
class ProductVariantAPIView(APIView):
    def get(self, request):
        product_variants = ProductVariant.objects.all()
        serializer = ProductVariantSerializer(product_variants, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.is_authenticated:
            serializer = ProductVariantSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Product Variant Attribute API
class ProductVariantAttributeAPIView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            # If the user is authenticated, show only their product variants
            variant_attributes = ProductVariant.objects.filter(created_by=request.user.vendor)
        else:
            # If the user is a guest (not authenticated), show all product variants
            variant_attributes = ProductVariant.objects.all()
        
        serializer = ProductVariantAttributeSerializer(variant_attributes, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.is_authenticated:
            serializer = ProductVariantAttributeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)