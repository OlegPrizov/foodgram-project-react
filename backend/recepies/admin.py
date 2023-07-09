from django.contrib import admin

from .models import Tag, User, Ingredient, Recipe

class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug'
    )

class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'password'
    )

class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )

class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'text',
        'name'
    )

admin.site.register(Tag, TagAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)