# Generated by Django 4.1.1 on 2022-11-15 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_contactsettings_contact_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='controlcenter',
            name='pickup_point_enabled',
            field=models.BooleanField(default=True, help_text='Enable or disable the pickup point field in checkout.', verbose_name='Pickup Point Enabled'),
        ),
        migrations.AddField(
            model_name='controlcenter',
            name='shipping_address_enabled',
            field=models.BooleanField(default=True, help_text='Enable or disable the shipping address field in checkout.', verbose_name='Shipping Address Enabled'),
        ),
    ]
