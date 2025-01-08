from rest_framework import serializers
from .models import Product, Attribute, AttributeValue, ProductVariant, ProductVariantAttribute
# from authentication_app.models import Vendor
from .models import Vendor


class ProductSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(queryset=Vendor.objects.all())  # Vendor reference
    variants = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,  # This makes 'variants' input-only
        required=True
    )  # List of variants (SKUs)
    attributes = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,  # This makes 'attributes' input-only
        required=True
    )  # List of attribute-value pairs

    class Meta:
        model = Product
        fields = ['id', 'name', 'created_by', 'variants', 'attributes']

    def create(self, validated_data):
    # Pop 'variants' and 'attributes' from the validated_data
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
        from itertools import product as cartesian_product
        attribute_combinations = list(cartesian_product(*attribute_dict.values()))

        for idx, attribute_combination in enumerate(attribute_combinations):
            # Generate a unique SKU using product name and index
            base_sku = variants_data[0] if variants_data else "VARIANT"
            unique_sku = f"{base_sku}-{idx + 1}"  # Ensure each SKU is unique

            variant = ProductVariant.objects.create(product=product, sku=unique_sku)

            for attribute_value in attribute_combination:
                ProductVariantAttribute.objects.create(
                    variant=variant,
                    attribute=attribute_value.attribute,
                    value=attribute_value
                )

        return product

