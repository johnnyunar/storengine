# Generated by Django 4.0.4 on 2022-06-26 21:11

from django.db import migrations
import wagtail_color_panel.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_brandsettings_cart_color_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brandsettings',
            name='accent_color',
            field=wagtail_color_panel.fields.ColorField(default='#FB8122', max_length=7, verbose_name='Accent Color'),
        ),
        migrations.AlterField(
            model_name='brandsettings',
            name='cart_color',
            field=wagtail_color_panel.fields.ColorField(default='#1D2938', max_length=7, verbose_name='Cart Color'),
        ),
        migrations.AlterField(
            model_name='brandsettings',
            name='cart_text_color',
            field=wagtail_color_panel.fields.ColorField(default='#FFFFFF', max_length=7, verbose_name='Cart Text Color'),
        ),
        migrations.AlterField(
            model_name='brandsettings',
            name='error_color',
            field=wagtail_color_panel.fields.ColorField(default='#FF7B76', help_text='The color of error messages in forms.', max_length=7, verbose_name='Error Color'),
        ),
        migrations.AlterField(
            model_name='brandsettings',
            name='primary_color',
            field=wagtail_color_panel.fields.ColorField(default='#1D2228', max_length=7, verbose_name='Primary Color'),
        ),
    ]
