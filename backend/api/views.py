from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from api import filters
from api.pagination import CustomPageNumberPagination
from api.serializers import (
    AddFavoriteRecipeSerializer, CreateRecipeSerializer, CustomUserSerializer,
    IngredientQuantity, IngredientSerializer, RecipeSerializer,
    SubscriptionSerializer, TagSerializer
)
from .permissions import IsAdminIsOwnerOrReadOnly
from djoser.views import UserViewSet

from recipes.models import (
    User, Tag, Ingredient, Recipe, Subscription, FavoriteRecipe, ShoppingCart
)


class CustomUserViewSet(UserViewSet):
    """Вьюсет для работы с User"""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminIsOwnerOrReadOnly, ]
    pagination_class = CustomPageNumberPagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
        url_name='subscribe',
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        change_status_subscription = Subscription.objects.filter(
            user=request.user.id, author=author.id
        )
        if request.method == 'POST':
            if request.user == author:
                return Response('Вы пытаетесь подписаться на себя!',
                                status=status.HTTP_400_BAD_REQUEST)
            if change_status_subscription.exists():
                return Response(f'Вы уже подписаны на {author}',
                                status=status.HTTP_400_BAD_REQUEST)
            subscribe = Subscription.objects.create(
                user=request.user,
                author=author
            )
            subscribe.save()
            serializer = SubscriptionSerializer(
                author, data=request.data,
                partial=True, context={'request': request}
            )
            serializer.is_valid()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if change_status_subscription.exists():
            change_status_subscription.delete()
            return Response(f'Вы отписались от {author}',
                            status=status.HTTP_204_NO_CONTENT)
        return Response(f'Вы не подписаны на {author}',
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['get'],
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=(IsAuthenticated,)
    )
    def get_subscriptions(self, request):
        """Возвращает авторов контента, на которых подписан
        текущий пользователь.."""
        subscriptions = Subscription.objects.filter(
            user=request.user
        ).values_list('author__id', flat=True)
        users = User.objects.filter(id__in=subscriptions)
        if users:
            page = self.paginate_queryset(users)
            serializer = SubscriptionSerializer(page, many=True,
                                                context={'request': request})
            return self.get_paginated_response(serializer.data)
        return Response('Вы ни на кого не подписаны.',
                        status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет работы с Tag"""

    permission_classes = (AllowAny,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы Ingredient"""

    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.IngredientFilter
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-created')
    serializer_class = RecipeSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAdminIsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.RecipeFilter

    def get_serializer_class(self):
        """Вызов определенного сериализатора взависимости от action"""

        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        elif self.action in ('create', 'partial_update'):
            return CreateRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='favorite',
        url_name='favorite',
    )
    def favorite(self, request, *args, **kwargs):
        """Добавить/удалить рецепт из избранного"""
        user = request.user
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        if request.method == 'POST':
            if FavoriteRecipe.objects.filter(
                    user=user, recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Вы уже добавили этот рецепт в избранное'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            FavoriteRecipe.objects.create(user=user, recipe=recipe)
            serializer = AddFavoriteRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            obj = FavoriteRecipe.objects.filter(user=user, recipe=recipe)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Этого рецепта нет у вас в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='shopping_cart',
        url_name='shopping_cart',
    )
    def shopping_cart(self, request, pk):
        """Метод для списка покупок"""

        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        obj = ShoppingCart.objects.filter(user=user, recipe__id=pk)
        if request.method == 'POST' and not obj.exists():
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = AddFavoriteRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'POST' and obj.exists():
            return Response(
                {'errors': 'Рецепт уже добавлен в список покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'DELETE':
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Рецепта нет в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def ingredients_to_txt(self, ingredients):
        shopping_list = ''
        for ingredient in ingredients:
            shopping_list += (
                f"{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['sum']}\n"
            )
        return shopping_list

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientQuantity.objects.filter(
            recipe__shopping_recipe__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(sum=Sum('amount'))
        shopping_list = self.ingredients_to_txt(ingredients)
        return HttpResponse(shopping_list, content_type='text/plain')
