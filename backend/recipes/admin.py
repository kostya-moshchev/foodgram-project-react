from django.contrib import admin
from .models import User, Tag, Ingredient, Recipe, IngredientQuantity, Subscription, FavoriteRecipe, ShoppingCart


#@admin.register(User)
#class UserAdmin(admin.ModelAdmin):
   # pass

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    pass

@admin.register(IngredientQuantity)
class IngredientQuantityAdmin(admin.ModelAdmin):
    pass

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    pass

@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    pass

@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    pass
