from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Ingredient, Recipe, RecipeIngredient, Tag


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug'
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit'
    )
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'author',
        'image',
        'ingredients_data',
        'tags',
        'favorite_count'
    )
    list_filter = ('author', 'name', 'tags',)
    inlines = [IngredientInline]

    @admin.display(description='Добавлений в избранное')
    def favorite_count(self, obj):
        return obj.favorite.count()

    @admin.display(description='Ингредиенты')
    def ingredients_data(self, obj):
        return list(obj.ingredients.all())

    def image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="80" height="60">')
