from rest_framework import serializers
from recipes.models import User, Tag, Ingredient, Recipe, IngredientQuantity, Subscription, FavoriteRecipe
from rest_framework.serializers import ModelSerializer



class CustomUserSerializer(UserCreateSerializer):
    """Сериализатор для модели User."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        """Мета-параметры сериализатора"""

        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        """Метод проверки подписки"""

        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода тэгов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода ингредиентов."""

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

    class Meta:
        model = Recipe
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = '__all__'


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer()

    class Meta:
        model = FavoriteRecipe
        fields = '__all__'


class AddFavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
