# Generated by Django 4.1.1 on 2022-09-24 14:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0023_cartitem_product_variant_squashed_0026_orderitem_product_variant'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ('name',), 'verbose_name': 'Product', 'verbose_name_plural': 'Products'},
        ),
    ]
