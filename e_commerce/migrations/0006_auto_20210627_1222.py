# Generated by Django 3.2.4 on 2021-06-27 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('e_commerce', '0005_categorie_view_count'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notederecommandation',
            options={'default_permissions': (), 'ordering': ['id'], 'permissions': (('add_note_recommandation', 'Ajouter une note de recommandation'),), 'verbose_name': 'Note de recommandation', 'verbose_name_plural': 'Notes de recommandation'},
        ),
        migrations.AlterModelOptions(
            name='produit',
            options={'default_permissions': (), 'ordering': ['id'], 'verbose_name': 'Produit', 'verbose_name_plural': 'Produits'},
        ),
        migrations.AddField(
            model_name='categorie',
            name='image',
            field=models.ImageField(blank=True, upload_to='categories/images'),
        ),
    ]
