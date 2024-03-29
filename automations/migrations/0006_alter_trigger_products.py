# Generated by Django 4.1.1 on 2022-11-03 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0032_remove_product_image'),
        ('automations', '0005_trigger_products'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trigger',
            name='products',
            field=models.ManyToManyField(blank=True, help_text='You can choose to fire this trigger for selected products only.', to='shop.product', verbose_name='Products'),
        ),
    ]
