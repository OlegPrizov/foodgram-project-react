from django.db.models import F, Sum

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from utils.functions import data_aggregartion, pdf_making
from utils.pagination import CustomPagination

from .filters import IngredientFilter, RecipeFilter
from .models import (
    Favorite, Ingredient,
    Recipe, RecipeIngredient,
    Shoplist, Tag
)
from .permissions import IsAuthorOrReadOnlyPermission
from .serializers import (
    FavoriteSerializer, IngredientShowSerializer, RecipeCreateSerializer,
    RecipeShowSerializer, ShopListSerializer, TagSerializer
)


class TagViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Tag.objects.all()
    pagination_class = None
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnlyPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeShowSerializer

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoplist__user=self.request.user).values(
                ingredient_name=F('ingredient__name'),
                measurement_unit=F('ingredient__measurement_unit')
        ).annotate(amount=Sum('amount')).values_list(
            'ingredient__name',
            'ingredient__measurement_unit',
            'amount'
        ).order_by('ingredient__name')
        return pdf_making(ingredients)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        return data_aggregartion(FavoriteSerializer, pk=pk, request=request)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        return data_aggregartion(ShopListSerializer, pk=pk, request=request)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        recipe = Recipe.objects.get(id=pk)
        fav = get_object_or_404(Favorite, user=request.user, recipe=recipe)
        fav.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        shop = get_object_or_404(Shoplist, user=request.user, recipe=recipe)
        shop.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
    permission_classes = (AllowAny,)
