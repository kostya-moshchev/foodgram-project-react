import csv

from django.core.management.base import BaseCommand

from backend.settings import CSV_FILES_DIR
from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Загрузка ингредиентов в базу данных'

    def handle(self, *args, **kwargs):
        with open(
            f'{CSV_FILES_DIR}/ingredients.csv', encoding='utf-8'
        ) as file:
            reader = csv.reader(file)
            ingredients = []
            for row in reader:
                ingredient = Ingredient(
                    name=row[0],
                    measurement_unit=row[1],
                )
                ingredients.append(ingredient)
            Ingredient.objects.bulk_create(ingredients)

        with open(
            f'{CSV_FILES_DIR}/tags.csv', encoding='utf-8'
        ) as file:
            reader = csv.reader(file)
            tags = []
            for row in reader:
                tag = Tag(
                    name=row[0],
                    color=row[1],
                    slug=row[2],
                )
                tags.append(tag)
            Tag.objects.bulk_create(tags)
