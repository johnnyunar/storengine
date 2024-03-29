# Generated by Django 4.0.4 on 2022-07-07 11:52

from django.db import migrations, models
import djrichtextfield.models


class Migration(migrations.Migration):

    dependencies = [
        ('mails', '0006_emailtemplate'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailtemplate',
            name='content',
            field=djrichtextfield.models.RichTextField(blank=True, null=True, verbose_name='Content'),
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='description',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='title',
            field=models.CharField(default='', max_length=128, verbose_name='Title'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='email',
            name='body',
            field=djrichtextfield.models.RichTextField(blank=True, null=True, verbose_name='Body'),
        ),
    ]
