# Generated by Django 4.2.3 on 2023-07-09 16:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recepies', '0004_recipeingridients_amount'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RecipeIngridients',
            new_name='RecipeIngredients',
        ),
    ]
