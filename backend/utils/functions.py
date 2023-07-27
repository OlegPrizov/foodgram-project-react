from recepies.models import Shoplist, RecipeIngredient
from django.db.models import Sum, F

def count_ingredients(obj):
    ingredients = RecipeIngredient.objects.filter(recipe__item__user=obj).values(
        ingredient_name=F('ingredient__name'),
        measurement_unit=F('ingredient__measurement_unit')
    ).annotate(
        amount=Sum('amount')
    ).values_list('ingredient__name', 'ingredient__measurement_unit', 'amount')
    return ingredients
