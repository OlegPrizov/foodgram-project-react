from colorfield.fields import ColorField

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from users.models import User
from utils.constants import RECIPE_APPM_MAX_LENGTH, MAX_VALIDATOR


class Tag(models.Model):
    """Тег."""

    name = models.CharField(
        'Название',
        max_length=RECIPE_APPM_MAX_LENGTH
    )
    color = ColorField(
        'Цвет',
        format='hex',
        null=True
    )
    slug = models.SlugField(
        'Слаг',
        unique=True,
        max_length=RECIPE_APPM_MAX_LENGTH,
        db_index=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингредиент."""

    name = models.CharField(
        'Название',
        max_length=RECIPE_APPM_MAX_LENGTH
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=RECIPE_APPM_MAX_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient',
            ),
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепт."""

    author = models.ForeignKey(
        User,
        related_name='recipes',
        verbose_name='Автор',
        on_delete=models.CASCADE
    )
    text = models.TextField(
        'Текст',
        help_text='Введите рецепт'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recepies/',
    )
    name = models.CharField(
        'Название',
        max_length=RECIPE_APPM_MAX_LENGTH
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(1, message='Укажите число больше нуля.'),
            MaxValueValidator(MAX_VALIDATOR, message='Укажите число меньше')
        ]
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTags',
        verbose_name='Теги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeTags(models.Model):
    """Связь рецепта и тега."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        Tag,
        verbose_name='Тег',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Связь рецепта и тега'

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class RecipeIngredient(models.Model):
    """Связь рецепта и ингредиента."""

    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredient',
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='ingredient_recipe',
        verbose_name='Ингредиент',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1,
                message='Введите число больше нуля.'
            ), MaxValueValidator(
                MAX_VALIDATOR,
                'Укажите менее большое значение.'
            )
        ],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.recipe} {self.ingredient} {self.amount}'


class UserRecipe(models.Model):
    """Вспомогательный класс для классов Favorite и ShopList."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True


class Favorite(UserRecipe):
    """Система избранного."""

    class Meta:
        verbose_name = 'Избранное'
        default_related_name = 'favorite'
        constraints = [
            UniqueConstraint(fields=['user', 'recipe'], name='unique_favorite')
        ]

    def __str__(self):
        return f'{self.user} добавил рецепт «{self.recipe}» в избранное'


class Shoplist(UserRecipe):
    """Корзина."""

    class Meta:
        verbose_name = 'Корзина'
        default_related_name = 'shoplist'
        constraints = [
            UniqueConstraint(fields=['user', 'recipe'], name='unique_shoplist')
        ]

    def __str__(self):
        return f'{self.user} добавил рецепт «{self.recipe}» в корзину'
