# Generated by Django 4.1.1 on 2022-09-28 19:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0031_productimage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='image',
        ),
    ]
