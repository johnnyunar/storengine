# Generated by Django 4.0.4 on 2022-06-22 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_contactsettings_email_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoogleFontSubset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=125, verbose_name='Name')),
            ],
        ),
        migrations.CreateModel(
            name='GoogleFontVariant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.PositiveIntegerField(verbose_name='Font Weight')),
                ('style', models.CharField(max_length=125, verbose_name='Font Style')),
                ('variant_id', models.CharField(max_length=125, unique=True, verbose_name='Variant ID')),
            ],
        ),
        migrations.CreateModel(
            name='GoogleFont',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('family', models.CharField(max_length=125, verbose_name='Font Family')),
                ('version', models.CharField(max_length=16, verbose_name='Font Version')),
                ('category', models.CharField(max_length=125, verbose_name='Font Category')),
                ('subsets', models.ManyToManyField(to='core.googlefontsubset', verbose_name='Font Subsets')),
                ('variants', models.ManyToManyField(to='core.googlefontvariant', verbose_name='Font Variants')),
            ],
        ),
    ]
