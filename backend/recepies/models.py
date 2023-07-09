from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

class User(AbstractUser):
    username = models.CharField('Username', max_length=150, unique=True, blank=False, null=False)
    email = models.EmailField('Email', max_length=254, null=False, blank=False)
    first_name = models.CharField('First name', max_length=150, null=False, blank=False)
    last_name = models.CharField('Last name', max_length=150, null=False, blank=False)
    REQUIRED_FIELDS = [
        'email',
        'first_name',
        'last_name',
    ]

class Tag(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=7, null=True)
    slug = models.SlugField(
        'слаг тега',
        unique=True,
        max_length=200,
        db_index=True,
    )

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=200) 
    measurement_unit = models.CharField(max_length=200)
    amount = models.IntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return self.name

class Recipe(models.Model):
    author = models.ForeignKey(
        User, related_name='recepies',
        on_delete=models.CASCADE
    )
    text = models.TextField(
        'текст',
        help_text='Введите рецепт'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recepies/',
    )
    name = models.CharField(max_length=200)
    cooking_time = models.IntegerField(validators=[MinValueValidator(1)])
    tags = models.ManyToManyField(Tag, through='RecipeTags')
#    ingridients = models.ForeignKey(
#        Ingredient,
#        related_name='recepies',
#        on_delete=models.CASCADE
#)

    def __str__(self):
        return self.name

class RecipeTags(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.recipe} {self.tag}'
 
class Follow(models.Model):
    """Система подписки"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='подписчик'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='автор'
    )

    def __str__(self):
        return f'Пользователь {self.user} подписался на {self.following}'

class Favorite(models.Model):
    """Система избранного"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='fan',
        verbose_name='подписчик'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='fav',
        verbose_name='избранное'
    )

    def __str__(self):
        return f'Пользователь {self.user} добавил рецепт «{self.recipe}» в избранное'

class Shoplist(models.Model):
    """Корзина"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='customer',
        verbose_name='клиент'
    )
    item = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='item',
        verbose_name='элемент'
    )

    def __str__(self):
        return f'Пользователь {self.user} добавил рецепт «{self.recipe}» в корзину'
