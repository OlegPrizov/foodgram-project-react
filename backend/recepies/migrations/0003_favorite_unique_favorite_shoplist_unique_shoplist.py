# Generated by Django 4.2.3 on 2023-08-03 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recepies', '0002_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_favorite'),
        ),
        migrations.AddConstraint(
            model_name='shoplist',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_shoplist'),
        ),
    ]