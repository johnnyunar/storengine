# Generated by Django 4.0.4 on 2022-06-26 19:23

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_remove_cart_total_price_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cartitem',
            options={'ordering': ('created_at',)},
        ),
        migrations.AddField(
            model_name='cartitem',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Created At'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cartitem',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated At'),
        ),
    ]