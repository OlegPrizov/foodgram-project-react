from djoser.serializers import UserCreateSerializer
from recepies.models import Recipe
from rest_framework import serializers

from .models import Follow, User


class UserCreateSerializer(UserCreateSerializer):
    """Создание пользователя"""

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        model = User


class NewUserSerializer(serializers.ModelSerializer):
    """Новое отображение пользователя"""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )
        model = User

    def get_is_subscribed(self, obj):
        """Подписан ли текущий пользователь на этого"""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, following=obj).exists()


class RecipeFollowShowSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецепта в подписках"""
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FollowShowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return Follow.objects.filter(user=user, following=obj).exists()

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        recipes_limit = self.context.get(
            'request'
            ).query_params.get(
            'recipes_limit'
        )
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return RecipeFollowShowSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
