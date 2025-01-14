# Generated by Django 4.2 on 2025-01-14 04:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
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
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=225)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=225)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_app.category')),
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
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_app.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductVariantAttribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_app.attribute')),
                ('value', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_app.attributevalue')),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_app.productvariant')),
            ],
        ),
    ]
