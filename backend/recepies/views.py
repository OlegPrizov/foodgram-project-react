import io

from django.http import FileResponse, HttpResponse

from django_filters.rest_framework import DjangoFilterBackend

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from users.models import User
from users.serializers import RecipeFollowShowSerializer

from utils.functions import count_ingredients
from utils.pagination import CustomPagination

from .filters import IngredientFilter, RecipeFilter
from .models import Favorite, Ingredient, Recipe, Shoplist, Tag
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnlyPermission
from .serializers import (IngredientShowSerializer, RecipeCreateSerializer,
                          RecipeShowSerializer, TagSerializer)


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
        pdfmetrics.registerFont(TTFont('FreeSans', './utils/FreeSans.ttf'))
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
