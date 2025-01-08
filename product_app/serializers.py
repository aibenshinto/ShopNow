from rest_framework import serializers
from .models import Product, Attribute, AttributeValue, ProductVariant, ProductVariantAttribute, Vendor

# Serializer for Product Variant
class ProductVariantSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False,allow_null=True)  # Optional image field

    class Meta:
        model = ProductVariant
        fields = ['sku', 'image']

# Update Product Serializer to include variants
class ProductSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(queryset=Vendor.objects.all())  # Vendor reference
    variants = ProductVariantSerializer(many=True, write_only=True, required=True)  # Handle variants
    attributes = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,  # This makes 'attributes' input-only
        required=True
    )  # List of attribute-value pairs

    class Meta:
        model = Product
        fields = ['id', 'name', 'created_by', 'variants', 'attributes']

    def create(self, validated_data):
        variants_data = validated_data.pop('variants')
        attributes_data = validated_data.pop('attributes')

        # Create the product
        product = Product.objects.create(**validated_data)

        # Process attributes and their values
        attribute_dict = {}
        for attribute_data in attributes_data:
            attribute_name = attribute_data.get('name')
            values = attribute_data.get('values')

            # Create or retrieve the attribute
            attribute, created = Attribute.objects.get_or_create(
                name=attribute_name,
                created_by=product.created_by
            )

            attribute_values = []
            for value in values:
                # Create or retrieve the attribute value
                attribute_value, created = AttributeValue.objects.get_or_create(
                    attribute=attribute,
                    value=value,
                    created_by=product.created_by
                )
                attribute_values.append(attribute_value)

            attribute_dict[attribute] = attribute_values

        # Create product variants based on attribute combinations
        attribute_combinations = list(cartesian_product(*attribute_dict.values()))

        for idx, attribute_combination in enumerate(attribute_combinations):
            # Automatically generate SKU using product name and attribute values
            attribute_names = [attribute.name for attribute in attribute_combination]
            base_sku = f"{product.name}-{'-'.join(attribute_names)}"
            
            # Generate the SKU as a string with product name and attribute name combination
            unique_sku = f"{base_sku}-{idx + 1}"

            variant_data = variants_data[idx] if variants_data else {}
            variant_image = variant_data.get('image')  # Get image data for variant

            variant = ProductVariant.objects.create(
                product=product,
                sku=unique_sku,
                image=variant_image  # Save image if provided
            )

            # Create ProductVariantAttributes for each attribute combination
            for attribute_value in attribute_combination:
                ProductVariantAttribute.objects.create(
                    variant=variant,
                    attribute=attribute_value.attribute,
                    value=attribute_value
                )

        return product
