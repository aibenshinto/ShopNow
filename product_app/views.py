from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from .models import Product, Attribute, AttributeValue, ProductVariant, ProductVariantAttribute
from .serializers import  ProductSerializer, AttributeSerializer, AttributeValueSerializer, ProductVariantSerializer, ProductVariantAttributeSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied
from authentication_app.models import Vendor

# Product API
class ProductAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.is_authenticated and (hasattr(request.user, 'vendor') or request.user.is_staff):
            data = request.data
            data['created_by'] = request.user.vendor.id
            serializer = ProductSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"detail": "Only vendors or admins can create product variant attributes."},
            status=status.HTTP_403_FORBIDDEN
        )

# Attribute API  
class AttributeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        attribute = Attribute.objects.all()
        serializer = AttributeSerializer(attribute, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        if request.user.is_authenticated and (hasattr(request.user, 'vendor') or request.user.is_staff):
            data = request.data
            data['created_by'] = request.user.vendor.id
            serializer = AttributeSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"detail": "Only vendors or admins can create product variant attributes."},
            status=status.HTTP_403_FORBIDDEN
        )

# Attribute Value API  
class AttributeValueAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        attributevalue = AttributeValue.objects.all()
        serializer = AttributeValueSerializer(attributevalue, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        if request.user.is_authenticated and (hasattr(request.user, 'vendor') or request.user.is_staff):
            data = request.data
            data['created_by'] = request.user.vendor.id
            serializer = AttributeValueSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"detail": "Only vendors or admins can create product variant attributes."},
            status=status.HTTP_403_FORBIDDEN
        )

# Product Variant API
class ProductVariantAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        product_variants = ProductVariant.objects.all() 
        serializer = ProductVariantSerializer(product_variants, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.is_authenticated and (hasattr(request.user, 'vendor') or request.user.is_staff):
            data = request.data
            data['created_by'] = request.user.vendor.id
            serializer = ProductVariantSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"detail": "Only vendors or admins can create product variant attributes."},
            status=status.HTTP_403_FORBIDDEN
        )
        
# Product Variant Attribute API
class ProductVariantAttributeCreateAPIView(generics.CreateAPIView):
    queryset = ProductVariantAttribute.objects.all()
    serializer_class = ProductVariantAttributeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        if self.request.user.is_authenticated and (hasattr(self.request.user, 'vendor') or self.request.user.is_staff):
            if hasattr(self.request.user, 'vendor'):
                # Vendor: Set the 'created_by' field to the vendor
                serializer.save(created_by=self.request.user.vendor)
            elif self.request.user.is_staff:
                # Admin: Admin can create without vendor context
                serializer.save(created_by=self.request.user)
            else:
                raise PermissionDenied({"detail": "Only vendors or admins can create product variant attributes."})
        else:
            raise PermissionDenied({"detail": "Authentication required."})

# Product Variant Attribute API
class ProductVariantAttributeAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductVariantAttribute.objects.all()
    serializer_class = ProductVariantAttributeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['variant__product', 'attribute', 'value']  # Fields to filter by
    search_fields = ['variant__product__name', 'attribute__name', 'value__value']  # Fields to search by

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if hasattr(self.request.user, 'vendor'):
                # Vendor: Only show their product variant attributes
                return ProductVariantAttribute.objects.filter(
                    variant__product__created_by=self.request.user.vendor
                )
            else:
                # Authenticated customers or admins: Show all
                return ProductVariantAttribute.objects.all()
        else:
            # Guest users: Show all
            return ProductVariantAttribute.objects.all()
        
    def perform_update(self, serializer):
        if self.request.user.is_authenticated and (hasattr(self.request.user, 'vendor') or self.request.user.is_staff):
            return super().perform_update(serializer)
        return Response(
            {"detail": "Only vendors or admins can update product variant attributes."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    def perform_destroy(self, instance):
        if self.request.user.is_authenticated and (hasattr(self.request.user, 'vendor') or self.request.user.is_staff):
            return super().perform_destroy(instance)
        return Response(
            {"detail": "Only vendors or admins can delete product variant attributes."},
            status=status.HTTP_403_FORBIDDEN
        )