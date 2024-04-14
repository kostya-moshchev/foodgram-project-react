from rest_framework import routers
from django.urls import path, include

from .views import (RecipeViewSet, IngredientViewSet,
                    TagViewSet, CustomUserViewSet)

app_name = 'api'

v1_router = routers.DefaultRouter()

v1_router.register(r'tags', TagViewSet, basename='tags')
v1_router.register(r'recipes', RecipeViewSet, basename='recipes')
v1_router.register(r'users', CustomUserViewSet, basename='users')
v1_router.register(r'ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
