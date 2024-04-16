from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from colorfield.fields import ColorField
from backend.constants import (EMAIL_LENGTH, NAME_LENGTH, TAG_NAME_LENGHT,
                               INGREDIENT_NAME_LENGHT, MEASUREMENT_LENGHT,
                               PECIPE_NAME, MIN_COOKING_TIME, MIN_AMOUNT)


class User(AbstractUser):
    """Модель пользователей"""

    email = models.EmailField(
        max_length=EMAIL_LENGTH,
        unique=True,
        blank=False,
        help_text='Введите email',
        verbose_name='Электронная почта',
    )
    first_name = models.CharField(
        max_length=NAME_LENGTH,
        verbose_name='Имя',
        blank=False,
    )
    last_name = models.CharField(
        max_length=NAME_LENGTH,
        verbose_name='Фамилия',
        blank=False,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return f"{self.username} {self.email}"


class Tag(models.Model):
    """Моедель тега"""
    name = models.CharField(
        max_length=TAG_NAME_LENGHT, unique=True, verbose_name='Название')
    color = ColorField(unique=True, verbose_name='Цветовой код')
    slug = models.SlugField(unique=True, verbose_name='Slug')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'color', 'slug'),
                name='unique_tags',
            ),
        )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингридиента"""
    name = models.CharField(
        max_length=INGREDIENT_NAME_LENGHT, verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MEASUREMENT_LENGHT, verbose_name='количество ингредиента'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredients'
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта"""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор')
    name = models.CharField(
        max_length=PECIPE_NAME, verbose_name='Название', blank=False)
    image = models.ImageField(
        upload_to='recipes/', blank=True, verbose_name='Картинка')
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientQuantity',
        verbose_name='Ингредиенты')
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(MIN_COOKING_TIME,
                              message='Минимальное значение 1!'),
        ])
    created = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации рецепта'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created',)

    def __str__(self):
        return self.name


class IngredientQuantity(models.Model):
    """Количество ингридиентов рецептах"""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='ingredient_list',)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(MIN_AMOUNT, message='Минимальное количество 1!'),
        ]
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredients_in_the_recipe'
            )
        ]


class Subscription(models.Model):
    """Модель подписок"""
    user = models.ForeignKey(
        User, related_name='follower',
        verbose_name='Подписчик', on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User, related_name='follow',
        verbose_name='Автор рецепта', on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ['user', 'author']
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} -> {self.author}'


class AbstractRelation(models.Model):
    """
    Абстрактная модель для отношений между пользователем и рецептом
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='%(class)s_related_user'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='%(class)s_related_recipe'
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            )
        ]


class FavoriteRecipe(AbstractRelation):
    """Модель для избранных рецептов"""

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.user} -> {self.recipe}'


class ShoppingCart(AbstractRelation):
    """Модель для списка покупок"""

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.user} {self.recipe}'


class TagInRecipe(models.Model):
    """Теги в рецептах"""
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Теги',
        help_text='Выберите теги рецепта'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Выберите рецепт')

    class Meta:
        """Параметры модели."""
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'
        constraints = [
            models.UniqueConstraint(fields=['tag', 'recipe'],
                                    name='unique_tagrecipe')
        ]

    def __str__(self):
        return f'{self.tag} {self.recipe}'
