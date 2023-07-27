from rest_framework import routers
from django.contrib import admin
from django.urls import path, include
from api.views import (
    TagViewSet, RecipeViewSet,
    IngredientViewSet, FollowListViewsSet,
    fav_recipe, follow, add_delete_shopcart
)
from django.conf import settings
from django.conf.urls.static import static

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
    import debug_toolbar

    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
