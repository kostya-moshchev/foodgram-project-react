from django.contrib.admin import ModelAdmin, register

from .models import (User, Tag, Ingredient, Recipe, Subscription,
                     FavoriteRecipe, ShoppingCart)


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = (
        'name', 'measurement_unit',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'name',
    )


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = (
        'name', 'author',
    )
    fields = (
        ('name', 'cooking_time',),
        ('author', 'tags',),
        ('text',),
        ('image',),
    )
    raw_id_fields = ('author', )
    search_fields = (
        'name', 'author',
    )
    list_filter = (
        'name', 'author__username',
    )


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = (
        'name', 'color', 'slug',
    )
    search_fields = (
        'name', 'color'
    )


@register(User)
class MyUserAdmin(ModelAdmin):

    list_display = ('pk', 'username', 'email', 'first_name', 'last_name',)
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    list_display = ('id', 'user', 'recipe')


@register(Subscription)
class FollowAdmin(ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')


@register(FavoriteRecipe)
class FavoriteAdmin(ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
