from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CheckConstraint, UniqueConstraint

from utils.constants import EMAIL_MAX_LENGTH, NAME_MAX_LENGTH


class User(AbstractUser):
    """Модель юзера"""
    username = models.CharField(
        'Логин',
        max_length=NAME_MAX_LENGTH,
        unique=True,
        blank=False,
        null=False
    )
    email = models.EmailField(
        'Почта',
        max_length=EMAIL_MAX_LENGTH,
        null=False,
        blank=False,
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=NAME_MAX_LENGTH,
        null=False,
        blank=False
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=NAME_MAX_LENGTH,
        null=False,
        blank=False
    )
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    USERNAME_FIELD = 'email'

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Пользователь',
        verbose_name_plural = 'Пользователи'

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

    class Meta:
        verbose_name = 'Подписки'
        constraints = [
            UniqueConstraint(
                fields=['user', 'following'],
                name='unique_follow'
            ),
            CheckConstraint(
                check=~models.Q(user=models.F("following")),
                name="prevent_self_follow"
            ),
        ]

    def __str__(self):
        return f'{self.user} подписался на {self.following}'
