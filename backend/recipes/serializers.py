from django.core.validators import MaxValueValidator, MinValueValidator
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
import webcolors

from users.serializers import NewUserSerializer
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, Shoplist,
                     Tag)
from utils.constants import MAX_VALIDATOR


class Hex2NameColor(serializers.Field):
    """Вспомогательный сериализатор для цвета тега."""

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения тега."""

    color = Hex2NameColor()

    class Meta:
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )
        model = Tag


class IngredientShowSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингридиента."""

    class Meta:
        fields = (
            'id',
            'name',
            'measurement_unit',
        )
        model = Ingredient


class IngredientShowInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиента в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )
        model = RecipeIngredient


class AddIngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиента в рецепт."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        validators=[
            MinValueValidator(1, message='Укажите число больше нуля.'),
            MaxValueValidator(MAX_VALIDATOR, message='Укажите число меньше.')
        ])

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта."""

    author = NewUserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField(required=False, allow_null=True)
    ingredients = AddIngredientInRecipeSerializer(many=True)
    cooking_time = serializers.IntegerField(
        validators=[
            MinValueValidator(1, message='Укажите число больше нуля.'),
            MaxValueValidator(32767, message='Укажите число меньше.')
        ])

    class Meta:
        fields = (
            'id', 'author',
            'name', 'image',
            'text', 'cooking_time',
            'tags', 'ingredients'
        )
        model = Recipe

    @staticmethod
    def add_ingredients(ingredients, recipe):
        bulk_ingredients = []
        for ingredient in ingredients:
            ingredient_data = ingredient.get('id')
            amount_data = ingredient.get('amount')
            bulk_ingredients.append(RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient_data,
                amount=amount_data
            ))
        RecipeIngredient.objects.bulk_create(bulk_ingredients)

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data, author=author)
        self.add_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    def to_representation(self, instance):
        return RecipeShowSerializer(instance, context=self.context).data

    def update(self, recipe, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        self.add_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return super().update(recipe, validated_data)


class RecipeShowSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецепта."""

    author = NewUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientShowInRecipeSerializer(
        source='recipe_ingredient',
        many=True
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        model = Recipe

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return obj.favorite.filter(user__id=request.user.id).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return obj.shoplist.filter(user__id=request.user.id).exists()


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления в избранное."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            return ValidationError('Такой рецепт уже добавлен в избранное')
        return data


class ShopListSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления в корзину."""

    class Meta:
        model = Shoplist
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if Shoplist.objects.filter(user=user, recipe=recipe).exists():
            return ValidationError('Такой рецепт уже добавлен в корзину')
        return data
