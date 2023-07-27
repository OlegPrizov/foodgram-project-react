import csv

from django.core.management.base import BaseCommand

from recepies.models import Ingredient


class Command(BaseCommand):
    help = 'Loading ingredients data from CSV file.'

    def handle(self, *args, **options):
        with open("../data/ingredients.csv", encoding='utf-8') as ingredients:
            file_reader = csv.reader(ingredients, delimiter=",")
            for row in file_reader:
                Ingredient.objects.create(name=row[0], measurement_unit=row[1])
