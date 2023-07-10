import re
import webcolors
from recepies.models import Tag, Recipe, User, Ingredient, Follow, RecipeTags, RecipeIngredient
import base64
from rest_framework import serializers
from django.core.files.base import ContentFile
from rest_framework.validators import UniqueTogetherValidator

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)

class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data

class UserSignupSerializer(serializers.ModelSerializer):
    username_regex = re.compile(r'^[\w\.\@\-\+]+\Z')

    class Meta:
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        model = User
        extra_kwargs = {
            'username': {'required': True, 'validators': []},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'required': True},
        }

    def validate(self, attrs):
        if not self.username_regex.match(attrs['username']):
            raise serializers.ValidationError(
                'username does not match pattern'
            )
        if len(attrs['username']) > 150:
            raise serializers.ValidationError(
                'username must be less than 151 character long'
            )
        if attrs['username'].lower() == 'me':
            raise serializers.ValidationError('"me" is not a valid username')
        queryset = User.objects.filter(username=attrs['username'])
        if queryset.exists():
            if not queryset.filter(email=attrs['email']).exists():
                raise serializers.ValidationError(
                    'username is already registered'
                )
        queryset = User.objects.filter(email=attrs['email'])
        if queryset.exists():
            if not queryset.filter(username=attrs['username']):
                raise serializers.ValidationError(
                    'email is already registered'
                )
        return attrs

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'email',
            'username',
            'first_name',
            'last_name'
        )
        model = User

class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения тега"""
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
    """Сериализатор для отображения ингридиента"""
    class Meta:
        fields = (
            'id',
            'name',
            'measurement_unit',
        )
        model = Ingredient

class IngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиента в рецепт"""
    amount = serializers.IntegerField()
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )
        model = RecipeIngredient

class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта"""
    author = UserSerializer(read_only=True, default=serializers.CurrentUserDefault())
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    image = Base64ImageField(required=False, allow_null=True)
    ingredients = IngredientCreateSerializer(many=True)

    class Meta:
        fields = (
            'id', 'author', 'name', 'image', 'text', 'cooking_time', 'tags', 'ingredients')
        model = Recipe
    
    def add_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            ingredient_data = ingredient.get('id')
            amount_data = ingredient.get('amount')
            RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient_data, amount=amount_data)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.add_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    def to_representation(self, instance):
        recipe = RecipeShowSerializer(instance).data
        return recipe

class RecipeShowSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientCreateSerializer(source = 'recipe_ingredient', many=True)
    image = Base64ImageField()

    class Meta:
        fields = (
            'id',
            'author',
            'name',
            'ingredients',
            'tags',
            'image',
            'text',
            'cooking_time'
        )
        model = Recipe

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.get(recipe=obj)
        return IngredientCreateSerializer(ingredients, many=True).data

class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all()
    )
    following = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Follow
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following')
            )
        ]

    def get_following(self, obj):
        obj.following=User.objects.get(pk=self.request.query_params.get('id'))
        return obj.following