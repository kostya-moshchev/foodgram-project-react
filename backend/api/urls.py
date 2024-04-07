from rest_framework import routers
from django.urls import path, include

from .views import RecipeViewSet, IngredientViewSet, TagViewSet, UserViewSet, UserViewSet

app_name = 'api'

auth_urls = [
    path('token/', TokenView.as_view()),
    path('signup/', AuthViewSet.as_view()),
]

v1_router = routers.DefaultRouter()

#reviews_url = r"titles/(?P<title_id>\d+)/reviews"
#comments_url = rf"{reviews_url}/(?P<review_id>\d+)/comments"

# v1_router.register(
    reviews_url, ReviewViewSet, basename='review'
)
# v1_router.register(
    comments_url, CommentViewSet, basename='comment'
)
v1_router.register(r'tags', TagViewSet, basename='tags')
# v1_router.register(r'categories', RecipeViewSet, basename='recipes')
v1_router.register(r'ingredients', IngredientViewSet, basename='ingredients')
# v1_router.register(r'titles', TagViewSet, basename='tags')
urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    # path('v1/auth/', include(auth_urls)),
]