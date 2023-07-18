from datetime import datetime

from dish_recipes.models import (Favorite, Ingredient, IngredientInRecipe,
                                 Recipe, ShoppingCart, Tag)
from django.db.models import QuerySet, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import IngredientFilter, RecipeFilter
from .paginators import CustomPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeReadSerializer,
                          RecipeShortSerializer, RecipeWriteSerializer,
                          TagSerializer)

RECIPE_COPY_ERROR = 'Рецепт уже был добавлен в избранное'
RECIPE_CART_COPY_ERROR = 'Рецепт уже был добавлен в корзину'
RECIPE_DELETE_ERROR = 'Рецепт уже был удален из избранного'
RECIPE_CART_DELETE_ERROR = 'Рецепт уже был удален из корзины'
CART_EXISTS_ERROR = 'Корзина пуста'


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class CartIngredientsQuerySet(QuerySet):
    def get_ingredients(self, user):
        return self.filter(
            recipe__shopping_cart__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, model, user, pk):
        model = Favorite
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {'errors': RECIPE_COPY_ERROR},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(
            user=user,
            recipe=recipe
        )
        serializer = RecipeShortSerializer(recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @favorite.mapping.delete
    def delete_favorite(self, model, user, pk):
        model = Favorite
        obj = model.objects.filter(
            user=user,
            recipe__id=pk
        )
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': RECIPE_DELETE_ERROR},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, model, user, pk):
        model = ShoppingCart
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {'errors': RECIPE_CART_COPY_ERROR},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(
            user=user,
            recipe=recipe
        )
        serializer = RecipeShortSerializer(recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, model, user, pk):
        model = ShoppingCart
        obj = model.objects.filter(
            user=user,
            recipe__id=pk
        )
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': RECIPE_CART_DELETE_ERROR},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        if not request.user.shopping_cart.exists():
            return Response(
                {'errors': CART_EXISTS_ERROR},
                status=HTTP_400_BAD_REQUEST
            )

        ingredients = IngredientInRecipe.objects.get_ingredients(request.user)

        today = datetime.today()
        shopping_list = (
            f'Список покупок для: {request.user.get_full_name()}\n\n'
            f'Дата: {today:%Y-%m-%d}\n\n'
        )
        shopping_list += '\n'.join([
            f'- {ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]})'
            f' - {ingredient["amount"]}'
            for ingredient in ingredients
        ])
        shopping_list += f'\n\nFoodgram ({today:%Y})'

        filename = f'{request.user.username}_shopping_list.txt'
        response = HttpResponse(
            shopping_list,
            content_type='text/plain'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response
