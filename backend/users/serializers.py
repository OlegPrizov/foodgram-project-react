from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Follow, User
from recipes.models import Recipe

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
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and obj.following.filter(user=request.user).exists()
        )


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


class FollowShowSerializer(NewUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = NewUserSerializer.Meta.fields + ('recipes', 'recipes_count')

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


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ('user', 'following')

    def validate(self, data):
        if data['user'] == data['following']:
            return ValidationError('Нельзя подписаться на самого себя')
        if Follow.objects.filter(
            user=data['user'],
            following=data['following']
        ).exists():
            return ValidationError('Вы уже подписаны на этого пользователя')
        return data
