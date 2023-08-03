import csv

from django.core.management.base import BaseCommand

from recepies.models import Tag

data = [
    ('Десерты', '#cc6699', 'desserts'),
    ('Напитки', '#339999', 'drinks'),
    ('Салаты', '#00cc66', 'salads'),
]

class Command(BaseCommand):
    help = 'Loading tags.'

    def handle(self, *args, **options):
            print('Загрузка началась')
            for name, color, slug in data:
                Tag.objects.get_or_create(name=name, color=color, slug=slug)
            print('Загрузка закончилась')