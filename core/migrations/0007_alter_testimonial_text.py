# Generated by Django 4.1.1 on 2022-09-24 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_contactsettings_gdpr_url_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testimonial',
            name='text',
            field=models.TextField(blank=True, null=True),
        ),
    ]
