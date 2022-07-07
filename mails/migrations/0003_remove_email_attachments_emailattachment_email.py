# Generated by Django 4.0.4 on 2022-07-06 17:56

from django.db import migrations
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('mails', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='email',
            name='attachments',
        ),
        migrations.AddField(
            model_name='emailattachment',
            name='email',
            field=modelcluster.fields.ParentalKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='email_attachments', to='mails.email'),
            preserve_default=False,
        ),
    ]
