# Generated by Django 3.2.4 on 2021-07-05 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aptusadmin', '0005_alter_customuser_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='email address'),
        ),
    ]
