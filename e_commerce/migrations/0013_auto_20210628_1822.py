# Generated by Django 3.2.4 on 2021-06-28 17:22

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('e_commerce', '0012_auto_20210628_1541'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logo', models.ImageField(blank=True, upload_to='images/logos')),
                ('site_primary_color', models.CharField(default='#3abbc2', max_length=7)),
                ('about_us_text', ckeditor.fields.RichTextField(blank=True)),
                ('email_reception_contact', models.EmailField(blank=True, max_length=254)),
                ('email_envoie_contact', models.EmailField(blank=True, max_length=254)),
                ('password_envoie_contact', models.CharField(blank=True, max_length=20)),
                ('tel_contact', models.CharField(blank=True, max_length=12)),
                ('adresse', models.CharField(blank=True, max_length=50)),
                ('horaires_travail', models.CharField(blank=True, max_length=20)),
                ('lien_facebook', models.CharField(blank=True, max_length=50)),
                ('lien_instagram', models.CharField(blank=True, max_length=50)),
                ('lien_twitter', models.CharField(blank=True, max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterModelOptions(
            name='imageslider',
            options={'verbose_name': 'Image du slider', 'verbose_name_plural': 'Images du slider'},
        ),
    ]
