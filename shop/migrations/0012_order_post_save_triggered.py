# Generated by Django 4.0.4 on 2022-07-07 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0011_delete_controlcenter'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='post_save_triggered',
            field=models.BooleanField(default=False),
        ),
    ]
