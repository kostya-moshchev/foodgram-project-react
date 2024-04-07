from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import (MinValueValidator, MaxValueValidator)


class User(AbstractUser):
    """Модель для пользователей"""

    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        db_index=True,
        verbose_name='Email',
        help_text='Введите email'
    )

    username = models.CharField(
        max_length=254,
        unique=True,
        blank=False,
        verbose_name='Логин',
        help_text='Введите ваш логин'
    )

    password = models.CharField(
        max_length=100,
        blank=False,
        verbose_name='Пароль',
        help_text='Введите пароль'
    )

    first_name = models.TextField(
        verbose_name='Имя',
        blank=False,
        null=False,
        help_text='Введите имя'
    )
    second_name = models.TextField(
        verbose_name='Фамилия',
        blank=False,
        null=False,
        help_text='Введите фамилию'
    )
    groups = None
    user_permissions = None

    def __str__(self):
        return self.username


class Tag(models.Model):
    """Моедель для тега"""
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')
    color = models.CharField(max_length=7, unique=True, verbose_name='Цветовой код')  # Например, #49B64E
    slug = models.SlugField(unique=True, verbose_name='Slug')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    """Модель для описание ингридиента"""
    name = models.CharField(max_length=255, verbose_name='Название')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Количество')
    measurement_unit = models.CharField(max_length=20, verbose_name='Единицы измерения')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    """Модель для описания рецепта"""
    # is_favorited # is_in_shopping_cart
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    name = models.CharField(max_length=255, verbose_name='Название')
    image = models.ImageField(upload_to='recipes/', blank=True, verbose_name='Картинка')
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(Ingredient, through='IngredientQuantity', verbose_name='Ингредиенты')
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(1, message='Минимальное значение 1!'),
            MaxValueValidator(300, message='Максимальное значение 300!')
        ])
    created = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации рецепта'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created',)


class IngredientQuantity(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Количество')
    unit = models.CharField(max_length=20, verbose_name='Единицы измерения')

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'


class Subscription(models.Model):
    """Модель для подписок"""
    subscriber = models.ForeignKey(
        User, related_name='subscriptions',
        verbose_name='Подписчик', on_delete=models.CASCADE
    )
    target_user = models.ForeignKey(
        User, related_name='subscribers_targets',
        verbose_name='Автор рецепта', on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['subscriber', 'target_user']

    def __str__(self):
        return f'{self.subscriber} -> {self.target_user}'


class FavoriteRecipe(models.Model):
    """модель для Избранного"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='favorite_recipes')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name='Рецепт', related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        unique_together = ['user', 'recipe']

    def __str__(self):
        return f'{self.user} -> {self.recipe}'


class ShoppingCart(models.Model):
    """Модель для описания формирования покупок """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_user',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_recipe',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        """Метод строкового представления модели."""

        return f'{self.user} {self.recipe}'

