from recepies.models import Shoplist, RecipeIngredient
from django.db.models import Sum, F

def count_ingredients(self, obj):
    RecipeIngredient.objects.values(
        ingredient_name=F('ingredient_name'),
        measurement_unit=F('ingredient__measurement_unit')
    ).annotate(
        amount=Sum('amount')
    )
    