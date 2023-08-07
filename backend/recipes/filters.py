from django_filters import rest_framework as filters

from .models import Ingredient, Recipe


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(
        method='get_favorite'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )

    class Meta:
        model = Recipe
        fields = [
            'is_favorited',
            'is_in_shopping_cart',
            'author',
            'tags'
        ]

    def get_favorite(self, queryset, name, value):
        if value:
            return queryset.filter(favorite__user=self.request.user)

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(
                shoplist__user=self.request.user
            )


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
