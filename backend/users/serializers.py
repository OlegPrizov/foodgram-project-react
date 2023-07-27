from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from .models import User, Follow


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
