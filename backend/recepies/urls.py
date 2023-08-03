from django.urls import include, path

from recepies.views import IngredientViewSet, RecipeViewSet, TagViewSet

from rest_framework import routers

app_name = 'recepies'

router = routers.DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recepies')

urlpatterns = [
    path('', include(router.urls)),
]
