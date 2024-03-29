# Generated by Django 4.0.4 on 2022-09-22 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_simplepage_menu_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pagesection',
            options={'verbose_name': 'Page Section', 'verbose_name_plural': 'Page Sections'},
        ),
        migrations.AddField(
            model_name='testimonial',
            name='video_url',
            field=models.URLField(blank=True, help_text='Shows after clicking "Watch" in the card.', null=True, verbose_name='Video URL'),
        ),
    ]
