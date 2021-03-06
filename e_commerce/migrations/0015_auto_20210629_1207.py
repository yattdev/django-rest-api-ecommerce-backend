# Generated by Django 3.2.4 on 2021-06-29 11:07

import ckeditor.fields
import colorfield.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('e_commerce', '0014_auto_20210628_1827'),
    ]

    operations = [
        migrations.AddField(
            model_name='imageslider',
            name='site_settings',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='e_commerce.sitesettings'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='about_us_text',
            field=ckeditor.fields.RichTextField(),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='adresse',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='email_envoie_contact',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='email_reception_contact',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='horaires_travail',
            field=models.CharField(max_length=45),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='lien_facebook',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='lien_instagram',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='lien_twitter',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='logo',
            field=models.ImageField(upload_to='images/logos'),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='nom_entreprise',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='password_envoie_contact',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='site_primary_color',
            field=colorfield.fields.ColorField(default='#3abbc2', max_length=18),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='tel_contact',
            field=models.CharField(max_length=20),
        ),
    ]
