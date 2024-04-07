from rest_framework.routers import DefaultRouter
from rest_framework import routers
from django.urls import path, include
from .views import RecipeViewSet, IngredientViewSet

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/recipes/download_shopping_cart/', RecipeViewSet.as_view({'get': 'download_shopping_cart'}), name='download_shopping_cart'),
    path('api/recipes/<int:pk>/shopping_cart/', RecipeViewSet.as_view({'post': 'shopping_cart'}), name='recipe_shopping_cart'),
]