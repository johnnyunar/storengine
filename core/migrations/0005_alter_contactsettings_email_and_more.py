# Generated by Django 4.0.4 on 2022-06-22 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_brandsettings_show_footer_waves'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactsettings',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='contactsettings',
            name='facebook',
            field=models.URLField(blank=True, help_text='Your Facebook page URL', null=True),
        ),
        migrations.AlterField(
            model_name='contactsettings',
            name='full_name',
            field=models.CharField(blank=True, default='Store Engine', max_length=64, verbose_name='Full Name'),
        ),
        migrations.AlterField(
            model_name='contactsettings',
            name='instagram',
            field=models.URLField(blank=True, help_text='Your Instagram Profile URL', null=True),
        ),
        migrations.AlterField(
            model_name='contactsettings',
            name='linkedin',
            field=models.URLField(blank=True, help_text='Your LinkedIn Profile URL', null=True),
        ),
        migrations.AlterField(
            model_name='contactsettings',
            name='phone_number',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='Phone Number'),
        ),
        migrations.AlterField(
            model_name='contactsettings',
            name='tiktok',
            field=models.URLField(blank=True, help_text='Your TikTok account URL', null=True),
        ),
        migrations.AlterField(
            model_name='contactsettings',
            name='trip_advisor',
            field=models.URLField(blank=True, help_text='Your Trip Advisor page URL', null=True),
        ),
        migrations.AlterField(
            model_name='contactsettings',
            name='youtube',
            field=models.URLField(blank=True, help_text='Your YouTube channel or user account URL', null=True),
        ),
    ]
