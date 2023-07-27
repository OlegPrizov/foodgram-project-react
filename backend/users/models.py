from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель юзера"""
    username = models.CharField(
        'Ник',
        max_length=150,
        unique=True,
        blank=False,
        null=False
    )
    email = models.EmailField(
        'Почта',
        max_length=254,
        null=False,
        blank=False
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        null=False,
        blank=False
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        null=False,
        blank=False
    )
    REQUIRED_FIELDS = [
        'email',
        'first_name',
        'last_name',
    ]

    def __str__(self):
        return self.get_full_name()


class Follow(models.Model):
    """Система подписки"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    def __str__(self):
        return f'{self.user} подписался на {self.following}'
