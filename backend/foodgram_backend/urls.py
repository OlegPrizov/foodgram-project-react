from rest_framework import routers
from django.contrib import admin
from django.urls import path, include
from api.views import TagViewSet, RecipeViewSet, FollowViewSet

router = routers.DefaultRouter()
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recepies')
router.register(r'users/(?P<id>\d+)/subscribe', FollowViewSet, basename='users')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]
