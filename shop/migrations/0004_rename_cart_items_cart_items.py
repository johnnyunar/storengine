# Generated by Django 4.0.4 on 2022-06-26 16:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_remove_address_address2_alter_address_address1'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cart',
            old_name='cart_items',
            new_name='items',
        ),
    ]