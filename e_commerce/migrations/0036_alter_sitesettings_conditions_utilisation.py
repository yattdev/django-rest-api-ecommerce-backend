# Generated by Django 3.2.4 on 2021-09-24 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('e_commerce', '0035_auto_20210706_1042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitesettings',
            name='conditions_utilisation',
            field=models.FileField(upload_to='fichiers/conditions_utilisation', verbose_name="Conditions d'utilisation"),
        ),
    ]
