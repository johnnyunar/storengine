# Generated by Django 4.0.4 on 2022-06-19 16:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_testimonial_is_active_alter_pagesection_section_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='testimonial',
            options={'verbose_name': 'Testimonial', 'verbose_name_plural': 'Testimonials'},
        ),
        migrations.RemoveField(
            model_name='testimonial',
            name='order',
        ),
    ]
