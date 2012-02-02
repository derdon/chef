from __future__ import with_statement

import pytest

from chef.datastructures import Ingredient, IngredientProperties, Ingredients


def test_ingredient_properties():
    properties = IngredientProperties(3, False, True)
    assert properties.value == 3
    assert not properties.is_dry
    assert properties.is_liquid


def test_ingredient():
    ingredient = Ingredient('apples', IngredientProperties(97, True, False))
    assert ingredient.name == 'apples'
    assert ingredient.properties.value == 97
    assert ingredient.properties.is_dry
    assert not ingredient.properties.is_liquid


class TestIngredients(object):
    def test_top(self, ingredients):
        assert ingredients.top == Ingredient(
            'water', IngredientProperties(250, False, True))

    def test_contains(self, ingredients):
        assert 'sugar' in ingredients
        assert 'water' in ingredients
        assert 'melon' not in ingredients


class TestIngredientsGetitem(object):
    def test_accessible(self, ingredients):
        assert ingredients['sugar'] == Ingredient(
            'sugar', IngredientProperties(120, True, False))
        assert ingredients['water'] == Ingredient(
            'water', IngredientProperties(250, False, True))

    def test_non_accessible(self, ingredients):
        with pytest.raises(KeyError) as e:
            ingredients['melon']
        assert e.value.message == 'melon'


class TestIngredientsSetitem(object):
    def test_existing(self, ingredients):
        ingredients['sugar'] = IngredientProperties(314, True, False)
        assert ingredients['sugar'] == Ingredient(
            'sugar', IngredientProperties(314, True, False))

    def test_new(self, ingredients):
        ingredients['flour'] = IngredientProperties(200, True, False)
        assert ingredients['flour'] == Ingredient(
            'flour', IngredientProperties(200, True, False))


class TestIngredientsStir(object):
    def setup_method(self, method):
        self.ingredients = Ingredients([
            Ingredient('first', IngredientProperties(1, True, False)),
            Ingredient('second', IngredientProperties(2, True, False)),
            Ingredient('third', IngredientProperties(3, True, False)),
            Ingredient('fourth', IngredientProperties(4, True, False)),
            Ingredient('fifth', IngredientProperties(5, True, False))])

    def test_one(self):
        self.ingredients.stir(1)
        assert self.ingredients == Ingredients([
            Ingredient('first', IngredientProperties(1, True, False)),
            Ingredient('second', IngredientProperties(2, True, False)),
            Ingredient('third', IngredientProperties(3, True, False)),
            Ingredient('fifth', IngredientProperties(5, True, False)),
            Ingredient('fourth', IngredientProperties(4, True, False))])

    def test_three(self):
        self.ingredients.stir(3)
        assert self.ingredients == Ingredients([
            Ingredient('first', IngredientProperties(1, True, False)),
            Ingredient('fifth', IngredientProperties(5, True, False)),
            Ingredient('second', IngredientProperties(2, True, False)),
            Ingredient('third', IngredientProperties(3, True, False)),
            Ingredient('fourth', IngredientProperties(4, True, False))])

    def test_no_modification(self):
        self.ingredients.stir(0)
        assert self.ingredients == Ingredients([
            Ingredient('first', IngredientProperties(1, True, False)),
            Ingredient('second', IngredientProperties(2, True, False)),
            Ingredient('third', IngredientProperties(3, True, False)),
            Ingredient('fourth', IngredientProperties(4, True, False)),
            Ingredient('fifth', IngredientProperties(5, True, False))])

    def test_too_damn_high(self):
        self.ingredients.stir(5)
        assert self.ingredients == Ingredients([
            Ingredient('fifth', IngredientProperties(5, True, False)),
            Ingredient('first', IngredientProperties(1, True, False)),
            Ingredient('second', IngredientProperties(2, True, False)),
            Ingredient('third', IngredientProperties(3, True, False)),
            Ingredient('fourth', IngredientProperties(4, True, False))])
