# Generated by Django 4.0.4 on 2022-06-22 15:40

import core.utils
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import functools


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CookiesPreferences',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('important_cookies_accepted', models.DateTimeField(verbose_name='Important Cookies Accepted')),
                ('analytic_cookies_accepted', models.DateTimeField(verbose_name='Analytic Cookies Accepted')),
                ('marketing_cookies_accepted', models.DateTimeField(verbose_name='Marketing Cookies Accepted')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
            ],
            options={
                'verbose_name': 'Cookies Preferences',
                'verbose_name_plural': 'Cookies Preferences',
            },
        ),
        migrations.CreateModel(
            name='ShopUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email')),
                ('first_name', models.CharField(max_length=100, verbose_name='First Name')),
                ('last_name', models.CharField(max_length=100, verbose_name='Last Name')),
                ('avatar', models.ImageField(blank=True, default='accounts/default-user.png', null=True, upload_to=functools.partial(core.utils.user_directory_path, *(), **{'subdir': 'avatar_images'}), verbose_name='Avatar')),
                ('newsletter_subscribe', models.BooleanField(default=False, verbose_name='Newsletter Subscription')),
                ('send_internal_notifications', models.BooleanField(default=False, help_text='E.g. New orders notifications.', verbose_name='Send Internal Messages')),
                ('is_staff', models.BooleanField(default=False, verbose_name='Is Staff')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date Joined')),
                ('cookies_preferences', models.OneToOneField(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.cookiespreferences', verbose_name='Cookies Preferences')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
        ),
    ]
