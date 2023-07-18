from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import QuerySet, Sum, UniqueConstraint

User = get_user_model()


FIELD_MAX_LENGTH = 200
HEX_MAX_LENGTH = 7
HEX_REGEX = '^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
HEX_VALIDATE_ERROR = 'Введенное значение не является цветом в формате HEX'
TIME_VALIDATE_ERROR = 'Нельзя указать время менее 1 минуты'
INGREDIENT_VALIDATE_ERROR = 'Не может быть менее 1 ингридиента'


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=FIELD_MAX_LENGTH
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=FIELD_MAX_LENGTH
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        'Название',
        unique=True,
        max_length=FIELD_MAX_LENGTH
    )
    color = models.CharField(
        'Цветовой HEX-код',
        unique=True,
        max_length=HEX_MAX_LENGTH,
        validators=[
            RegexValidator(
                regex=HEX_REGEX,
                message=HEX_VALIDATE_ERROR
            )
        ]
    )
    slug = models.SlugField(
        'Уникальный slug',
        max_length=FIELD_MAX_LENGTH,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        'Название',
        max_length=FIELD_MAX_LENGTH
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Автор',
    )
    text = models.TextField(
        'Описание'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='dish_recipes/'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(
                1,
                message=TIME_VALIDATE_ERROR
            )
        ]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )

    class Meta:
        ordering = ['-id']
        related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class CartIngredientsQuerySet(QuerySet):
    def get_ingredients(self, user):
        return self.filter(
            recipe__shopping_cart__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_list',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                1,
                message=INGREDIENT_VALIDATE_ERROR
            )
        ]
    )
    objects = CartIngredientsQuerySet.as_manager()

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return (
            f'{self.ingredient.name} ({self.ingredient.measurement_unit})'
            f' - {self.amount} '
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'Пользователь {self.user} добавил "{self.recipe}" в Избранное'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        related_name = 'shopping_cart'
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'Пользователь {self.user} добавил "{self.recipe}" к покупкам'
