import csv

from django.core.management.base import BaseCommand

from backend.settings import CSV_FILES_DIR
from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Загрузка ингредиентов в базу данных'

    def handle(self, *args, **kwargs):
        self.load_ingredients()
        self.load_tags()

    def load_ingredients(self):
        with open(
            f'{CSV_FILES_DIR}/ingredients.csv', encoding='utf-8'
        ) as file:
            reader = csv.reader(file)
            ingredients = []
            for row in reader:
                if not Ingredient.objects.filter(
                 name=row[0], measurement_unit=row[1]).exists():
                    ingredient = Ingredient(
                        name=row[0],
                        measurement_unit=row[1],
                    )
                    ingredients.append(ingredient)
            if ingredients:
                Ingredient.objects.bulk_create(ingredients)

    def load_tags(self):
        with open(
            f'{CSV_FILES_DIR}/tags.csv', encoding='utf-8'
        ) as file:
            reader = csv.reader(file)
            tags = []
            for row in reader:
                if not Ingredient.objects.filter(name=row[0]).exists():
                    tag = Tag(
                        name=row[0],
                        color=row[1],
                        slug=row[2],
                    )
                tags.append(tag)
            if tags:
                Tag.objects.bulk_create(tags)
