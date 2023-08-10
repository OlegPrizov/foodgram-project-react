import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Loading ingredients data from CSV file.'

    def handle(self, *args, **options):
        with open('./data/ingredients.csv', encoding='utf-8') as ingredients:
            file_reader = csv.reader(ingredients, delimiter=',')
            print('Загрузка началась')
            for name, measurement_unit in file_reader:
                Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit
                )
            print('Загрузка закончилась')
