# Generated by Django 3.2.4 on 2021-07-01 07:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('e_commerce', '0021_client_date_expiration'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='client',
            options={'default_permissions': (), 'ordering': [], 'verbose_name': 'Client', 'verbose_name_plural': 'Clients'},
        ),
        migrations.RemoveField(
            model_name='client',
            name='code_sec',
        ),
        migrations.RemoveField(
            model_name='client',
            name='date_expiration',
        ),
        migrations.RemoveField(
            model_name='client',
            name='num_cart',
        ),
    ]
