# Generated by Django 4.1.1 on 2022-09-23 10:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0016_product_preorder_end_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'verbose_name': 'Product', 'verbose_name_plural': 'Products'},
        ),
    ]
