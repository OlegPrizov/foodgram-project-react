import re
import webcolors
from recepies.models import Tag, Recipe, User, Ingredient, Follow, RecipeTags, RecipeIngredient, Shoplist, Favorite
import base64
from rest_framework import serializers
from django.core.files.base import ContentFile
from rest_framework.validators import UniqueTogetherValidator

class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        model = User

class NewUserSerializer(serializers.ModelSerializer):
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
        return Follow.objects.filter(user=user, following=obj).exists()