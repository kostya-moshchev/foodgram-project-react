import base64
from django.core.files.base import ContentFile

from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers
from recipes.models import (
    User, Tag, Ingredient, Recipe, TagInRecipe, ShoppingCart,
    IngredientQuantity, Subscription, FavoriteRecipe
)


class Base64ImageField(serializers.ImageField):
    """Кодирование изображения в base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='photo.' + ext)

        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    """Сериализатор модели User"""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:

        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        """Проверка подписки"""

        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj.id).exists()


class CustomCreateUserSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя"""
    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тэгов"""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов"""

    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('id', 'name', 'measurement_unit',)


class IngredientQuantitySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientQuantity
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов"""
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientQuantitySerializer(
        source='ingredient_list', many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time'
                  )

    def get_is_favorited(self, obj):
        """Проверка на добавление в избранное"""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Возвращает объекты в корзине"""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()


class CreateIngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов в рецептах"""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

    class Meta:

        model = IngredientQuantity
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецептов"""

    ingredients = CreateIngredientsInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField(use_url=True)

    class Meta:

        model = Recipe
        fields = ('ingredients', 'tags', 'name',
                  'image', 'text', 'cooking_time')

    def to_representation(self, instance):

        serializer = RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        )
        return serializer.data

    def validate(self, data):
        """Метод валидации ингредиентов"""

        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')

        if not ingredients:
            raise serializers.ValidationError(
                'Необходим хотя бы один ингредиент'
            )
        unique_ingredients = set(
            ingredient['id'] for ingredient in ingredients)
        if len(unique_ingredients) != len(ingredients):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальными!'
            )
        if not tags:
            raise serializers.ValidationError(
                'Необходим хотя бы один тег'
            )
        unique_tags = set(tag for tag in tags)
        if len(unique_tags) != len(tags):
            raise serializers.ValidationError(
                'Теги должны быть уникальными!'
            )
        return data

    def create_ingredients(self, ingredients, recipe):
        """Метод создания ингредиента"""

        if not ingredients:
            raise serializers.ValidationError(
                'Рецепт должен содержать ингредиенты!'
            )
        ingredientsquantity = []
        for element in ingredients:
            id = element['id']
            try:
                ingredient = Ingredient.objects.get(pk=id)
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    'Нет такого ингредиента!'
                )
            amount = element['amount']
            ingredientquantity = IngredientQuantity(
                ingredient=ingredient, recipe=recipe, amount=amount
            )
            ingredientsquantity.append(ingredientquantity)
        IngredientQuantity.objects.bulk_create(ingredientsquantity)

    def create(self, validated_data):
        """Метод создания модели"""

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        user = self.context.get('request').user
        recipe = Recipe.objects.create(**validated_data, author=user)
        self.create_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        """Метод обновления модели"""

        IngredientQuantity.objects.filter(recipe=instance).delete()
        TagInRecipe.objects.filter(recipe=instance).delete()

        self.create_ingredients(validated_data.pop('ingredients'), instance)
        instance.tags.set(validated_data.pop('tags'))

        return super().update(instance, validated_data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор избранного"""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        read_only_fields = (
            'name',
            'image',
            'cooking_time',
        )


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавления в избранное"""
    class Meta:
        model = FavoriteRecipe
        fields = (
            'user',
            'recipe'
        )

    def validate(self, attrs):
        user = attrs['user']
        recipe = attrs['recipe']

        if FavoriteRecipe.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'recipe': 'Вы уже добавили этот рецепт в избранное'}
            )
        return attrs

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class ShoppingCartRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавления в избранное"""
    class Meta:
        model = ShoppingCart
        fields = (
            'user',
            'recipe'
        )

    def validate(self, attrs):
        user = attrs['user']
        recipe = attrs['recipe']

        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'recipe': 'Вы уже добавили этот рецепт в корзину'}
            )
        return attrs

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class SubscriptionSerializer(CustomUserSerializer):
    """Сериализатор Subscription"""

    recipes = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count',)

    def validate(self, attrs):
        author = self.instance
        subscriber = self.context['request'].user
        if Subscription.objects.filter(
            user=subscriber.id, author=author.id
        ).exists():
            raise serializers.ValidationError(
                {f'Вы уже подписаны на {author}'}
            )
        if subscriber == author:
            raise serializers.ValidationError(
                'Вы пытаетесь подписаться на себя!'
            )
        return attrs

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = Recipe.objects.filter(author=obj)
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return ShortRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        recipes = Recipe.objects.filter(author=obj)
        return recipes.count()
