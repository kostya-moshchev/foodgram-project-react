import base64

from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers
from recipes.models import User, Tag, Ingredient, Recipe, IngredientQuantity, Subscription, FavoriteRecipe
from rest_framework.serializers import ModelSerializer
from rest_framework.fields import SerializerMethodField


class Base64ImageField(serializers.ImageField):
    """Кодирование изображения в base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='photo.' + ext)

        return super().to_internal_value(data)

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
        return Subscription.objects.filter(user=user, author=obj.id).exists()


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
        read_only_fields = ('id', 'name', 'measurement_unit',)


class IngredientQuantitySerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()

    class Meta:
        model = IngredientQuantity
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    author = UserSerializer(
        read_only=True
    )
    ingredients = IngredientSerializer(
        source='ingredient_amounts',
        many=True,
        read_only=True
    )
    image = Base64ImageField()
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
