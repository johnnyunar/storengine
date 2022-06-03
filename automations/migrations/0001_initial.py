# Generated by Django 4.0.4 on 2022-06-03 20:39

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_id', models.CharField(max_length=32, verbose_name='Action ID')),
                ('name', models.CharField(max_length=32, verbose_name='Name')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_%(app_label)s.%(class)s_set+', to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'Action',
                'verbose_name_plural': 'Actions',
            },
        ),
        migrations.CreateModel(
            name='Trigger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trigger_type', models.CharField(choices=[('new_user', 'New User'), ('new_order', 'New Order'), ('new_quiz_record', 'New Quiz Record')], max_length=64, verbose_name='Trigger Type')),
                ('name', models.CharField(max_length=32, verbose_name='Name')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
            ],
            options={
                'verbose_name': 'Trigger',
                'verbose_name_plural': 'Triggers',
            },
        ),
        migrations.CreateModel(
            name='EmailAction',
            fields=[
                ('action_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='automations.action')),
                ('recipients', django.contrib.postgres.fields.ArrayField(base_field=models.EmailField(max_length=254), blank=True, help_text='Enter a list of email addresses divided by a comma. In case of trigger notifications, this list will be used instead of the trigger recipient data.', null=True, size=None, verbose_name='Recipients')),
                ('is_trigger_notification', models.BooleanField(verbose_name='Trigger Notification')),
                ('is_internal_notification', models.BooleanField(verbose_name='Internal Notification')),
            ],
            options={
                'verbose_name': 'Email Action',
                'verbose_name_plural': 'Email Actions',
            },
            bases=('automations.action',),
        ),
        migrations.CreateModel(
            name='Automation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='Name')),
                ('is_active', models.BooleanField(default=False, verbose_name='Is Active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('actions', models.ManyToManyField(to='automations.action', verbose_name='Actions')),
                ('trigger', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='automations.trigger', verbose_name='Trigger')),
            ],
            options={
                'verbose_name': 'Automation',
                'verbose_name_plural': 'Automations',
            },
        ),
    ]
