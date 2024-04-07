import django_filters
from recipes.models import Recipe

class RecipeFilter(django_filters.FilterSet):
    class Meta:
        model = Recipe
        fields = {
            'author': ['exact'],
            'is_favorite': ['exact'],
            'is_in_shopping_cart': ['exact'],
            'tags': ['exact'],
            # Другие поля, по которым нужно фильтровать
        }