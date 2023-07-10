# Generated by Django 4.2.3 on 2023-07-09 16:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recepies', '0002_remove_recipe_tags_recipe_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingredient',
            name='amount',
        ),
        migrations.CreateModel(
            name='RecipeIngridients',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recepies.ingredient')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recepies.recipe')),
            ],
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(through='recepies.RecipeIngridients', to='recepies.ingredient'),
        ),
    ]
