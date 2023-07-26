from recepies.models import Shoplist, RecipeIngredient
from django.db.models import Sum, F

def count_ingredients(self, obj):
    RecipeIngredient.objects.filter(recipe__item__user=self.request.user).values(
        ingredient_name=F('ingredient_name'),
        measurement_unit=F('ingredient__measurement_unit')
    ).annotate(
        amount=Sum('amount')
    ).values_list('ingredient__name', 'ingredient__measurement_unit', 'amount')
    