from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from recepies.views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                            add_delete_shopcart, fav_recipe)

from rest_framework import routers

from users.views import FollowListViewsSet, follow

router = routers.DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recepies')
router.register(
    r'users/subscriptions',
    FollowListViewsSet,
    basename='subscriptions'
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('api/recipes/<int:id>/favorite/', fav_recipe, name='fav_recipe'),
    path('api/users/<int:pk>/subscribe/', follow, name='follow'),
    path(
        'api/recipes/<int:id>/shopping_cart/',
        add_delete_shopcart,
        name='shopcart'
    ),
]

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
