# Generated by Django 4.0.4 on 2022-06-22 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_brandsettings_show_footer_waves'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brandsettings',
            name='show_footer_waves',
            field=models.BooleanField(default=False, verbose_name='Show Footer Waves'),
        ),
    ]
