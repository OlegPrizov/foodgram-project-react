from django.shortcuts import render
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework import mixins
from recepies.models import Tag, Recipe, User, Ingredient, Favorite, Shoplist, RecipeIngredient, Follow
from .serializers import TagSerializer, RecipeCreateSerializer, RecipeShowSerializer, FollowSerializer, IngredientShowSerializer, FollowShowSerializer, RecipeFollowShowSerializer
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import HttpResponse
from django.db.models import Sum, F
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        print(context)
        return context

class IngredientViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = IngredientShowSerializer
    pagination_class = None
    queryset = Ingredient.objects.all()

class FollowViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet    
    ):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(*args, **kwargs)

@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def follow(request, pk):
    user = get_object_or_404(User, username=request.user.username)
    following = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        if user.id == following.id:
            return Response('Нельзя подписаться на самого себя', status=status.HTTP_400_BAD_REQUEST)
        elif Follow.objects.filter(user=user, following=following).exists():
            return Response('Вы уже подписаны на этого пользователя', status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.create(user=user, following=following)
        to_serializer = User.objects.get(username=following)
        serializer = FollowShowSerializer(to_serializer, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    if request.method == 'DELETE':
        try:
            subscription = Follow.objects.get(user=user, following=following)
        except ObjectDoesNotExist:
            return Response('Вы не подписаны на этого пользователя', status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return HttpResponse ('Вы отписались от пользователя', status=status.HTTP_204_NO_CONTENT)

class FollowListViewsSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = FollowShowSerializer
    queryset = User.objects.all()
    pagination_class = PageNumberPagination

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(following__user=user)

@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def fav_recipe(request, id):
    user = get_object_or_404(User, username=request.user.username)
    recipe = get_object_or_404(Recipe, pk=id)

    if request.method == 'POST':
        Favorite.objects.create(user=user, recipe=recipe)
        serializer = RecipeFollowShowSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    if request.method == 'DELETE':
        fav = Favorite.objects.get(user=user, recipe=recipe)
        fav.delete()
        return HttpResponse (status=status.HTTP_204_NO_CONTENT)

@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def add_delete_shopcart(request, id):
    user = get_object_or_404(User, username=request.user.username)
    recipe = get_object_or_404(Recipe, pk=id)

    if request.method == 'POST':
        Shoplist.objects.create(user=user, item=recipe)
        serializer = RecipeFollowShowSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    if request.method == 'DELETE':
        fav = Shoplist.objects.get(user=user, item=recipe)
        fav.delete()
        return HttpResponse (status=status.HTTP_204_NO_CONTENT)

