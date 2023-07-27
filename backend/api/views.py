from rest_framework import mixins, permissions, status, viewsets
from rest_framework.generics import get_object_or_404
from recepies.models import Tag, Recipe, Ingredient, Favorite, Shoplist
from users.models import User, Follow
from .serializers import (
    TagSerializer, RecipeCreateSerializer,
    RecipeShowSerializer, IngredientShowSerializer,
    FollowShowSerializer, RecipeFollowShowSerializer
)
from .pagination import CustomPagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from .permissions import IsAuthorOrReadOnlyPermission, IsAdminOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from utils.functions import count_ingredients
from .filters import RecipeFilter, IngredientFilter
from rest_framework.decorators import action
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter


class TagViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Tag.objects.all()
    pagination_class = None
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnlyPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeShowSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        pdfmetrics.registerFont(TTFont('FreeSans', './api/FreeSans.ttf'))
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
        textob = c.beginText()
        textob.setTextOrigin(inch, inch)
        textob.setFont('FreeSans', 14)
        ingredients = count_ingredients(self.request.user)
        data = []
        for ingredient in ingredients:
            data.append(str(
                f'{ingredient[0]} {ingredient[2]} {ingredient[1]}'
            ))
        for line in data:
            textob.textLine(line)
        c.drawText(textob)
        c.showPage()
        c.save()
        buf.seek(0)
        return FileResponse(buf, as_attachment=True, filename='recipes.pdf')


class IngredientViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = IngredientShowSerializer
    pagination_class = None
    queryset = Ingredient.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (IsAdminOrReadOnly,)


@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def follow(request, pk):
    user = get_object_or_404(User, username=request.user.username)
    following = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        if user.id == following.id:
            return Response(
                'Нельзя подписаться на самого себя',
                status=status.HTTP_400_BAD_REQUEST
            )
        elif Follow.objects.filter(user=user, following=following).exists():
            return Response(
                'Вы уже подписаны на этого пользователя',
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.create(user=user, following=following)
        to_serializer = User.objects.filter(username=following)
        serializer = FollowShowSerializer(
            to_serializer,
            context={'request': request},
            many = True
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    if request.method == 'DELETE':
        try:
            subscription = Follow.objects.get(user=user, following=following)
        except ObjectDoesNotExist:
            return Response(
                'Вы не подписаны на этого пользователя',
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return HttpResponse(
            'Вы отписались от пользователя',
            status=status.HTTP_204_NO_CONTENT
        )


class FollowListViewsSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = FollowShowSerializer
    queryset = User.objects.all()
    pagination_class = CustomPagination

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
        fav = Favorite.objects.filter(user=user, recipe=recipe)
        fav.delete()
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)


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
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)
