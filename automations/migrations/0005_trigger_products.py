# Generated by Django 4.1.1 on 2022-11-03 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0032_remove_product_image'),
        ('automations', '0004_alter_action_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='trigger',
            name='products',
            field=models.ManyToManyField(help_text='You can choose to fire this trigger for selected products only.', to='shop.product', verbose_name='Products'),
        ),
    ]