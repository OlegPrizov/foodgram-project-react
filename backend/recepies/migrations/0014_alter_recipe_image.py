# Generated by Django 4.2.3 on 2023-07-25 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recepies', '0013_alter_ingredient_options_alter_tag_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to='recepies/photos/', verbose_name='Картинка'),
        ),
    ]
