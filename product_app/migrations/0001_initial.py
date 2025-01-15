# Generated by Django 4.2 on 2025-01-15 04:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('vendor', '0001_initial'),
        ('authentication_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=225)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication_app.vendor')),
            ],
        ),
        migrations.CreateModel(
            name='AttributeValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=225)),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_app.attribute')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication_app.vendor')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=225)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vendor.category')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication_app.vendor')),
            ],
        ),
        migrations.CreateModel(
            name='ProductVariant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sku', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='product_variant_images/')),
                ('price', models.IntegerField(null=True)),
                ('stock', models.IntegerField(null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication_app.vendor')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_app.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductVariantAttribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_app.attribute')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication_app.vendor')),
                ('value', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_app.attributevalue')),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_app.productvariant')),
            ],
        ),
    ]
