# Generated by Django 4.0.4 on 2022-06-24 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_simplepage_seo_keywords'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='seo_keywords',
            field=models.CharField(blank=True, help_text='Keywords for search engines. Like: food, friends, traveling', max_length=512, null=True, verbose_name='Keywords'),
        ),
    ]
