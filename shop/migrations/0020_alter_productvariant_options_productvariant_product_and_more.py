# Generated by Django 4.1.1 on 2022-09-23 14:23

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0019_product_product_id_product_related_products_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productvariant',
            options={'verbose_name': 'Product Variant', 'verbose_name_plural': 'Product Variants'},
        ),
        migrations.AddField(
            model_name='productvariant',
            name='product',
            field=modelcluster.fields.ParentalKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='shop.product'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productvariant',
            name='sort_order',
            field=models.IntegerField(blank=True, editable=False, null=True),
        ),
    ]