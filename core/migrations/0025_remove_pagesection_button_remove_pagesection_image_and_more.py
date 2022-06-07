# Generated by Django 4.0.4 on 2022-06-07 18:17

from django.db import migrations, models
import django.db.models.deletion
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0024_index_image_file_hash'),
        ('core', '0024_remove_contactsection_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pagesection',
            name='button',
        ),
        migrations.RemoveField(
            model_name='pagesection',
            name='image',
        ),
        migrations.RemoveField(
            model_name='pagesection',
            name='text',
        ),
        migrations.CreateModel(
            name='BasicPageSection',
            fields=[
                ('pagesection_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.pagesection')),
                ('text', wagtail.fields.RichTextField(verbose_name='Text')),
                ('button', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.button', verbose_name='Button')),
                ('image', models.ForeignKey(blank=True, help_text='This image will show up on the right side of the section.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', verbose_name='Image')),
            ],
            bases=('core.pagesection',),
        ),
    ]
