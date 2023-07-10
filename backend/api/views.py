from django.shortcuts import render
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework import mixins
from recepies.models import Tag, Recipe, User, Ingredient
from .serializers import TagSerializer, RecipeCreateSerializer, RecipeShowSerializer, FollowSerializer, IngredientShowSerializer
from rest_framework.pagination import LimitOffsetPagination

class TagViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeShowSerializer

class IngredientViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = IngredientShowSerializer
    queryset = Ingredient.objects.all()

class FollowViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet    
    ):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(following=User.objects.get(pk=self.request.query_params.get('following')))
