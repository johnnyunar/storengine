# Generated by Django 4.0.4 on 2022-06-28 17:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_contactsettings_business_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='siteconfiguration',
            name='footer_image',
        ),
        migrations.RemoveField(
            model_name='siteconfiguration',
            name='hero_video',
        ),
        migrations.RemoveField(
            model_name='siteconfiguration',
            name='notification_bar_show',
        ),
        migrations.RemoveField(
            model_name='siteconfiguration',
            name='notification_bar_text',
        ),
    ]
