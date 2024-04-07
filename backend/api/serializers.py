from rest_framework import serializers
from recipes.models import Tag, Ingredient, Recipe, IngredientQuantity, Subscription, FavoriteRecipe
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'

class IngredientQuantitySerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()

    class Meta:
        model = IngredientQuantity
        fields = '__all__'

class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientQuantitySerializer(many=True)
    tags = TagSerializer(many=True)
    author = UserSerializer()

    class Meta:
        model = Recipe
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    subscriber = UserSerializer()
    target_user = UserSerializer()

    class Meta:
        model = Subscription
        fields = '__all__'

class FavoriteRecipeSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    recipe = RecipeSerializer()

    class Meta:
        model = FavoriteRecipe
        fields = '__all__'
