from __future__ import with_statement

try:
    from collections import namedtuple
except ImportError:
    from namedtuple_recipe import namedtuple

IngredientProperties = namedtuple(
    'IngredientProperties', 'value is_dry is_liquid')
Ingredient = namedtuple('Ingredient', 'name properties')

Recipe = namedtuple(
    'Recipe',
    'ingredients cooking_time oven_temperature instructions serves')


def prettify_namedtuple(namedtuple_cls, breaking=True):
    def func(self, p, cycle):
        name = namedtuple_cls.__name__
        if cycle:
            p.text('%s(...)' % name)
        else:
            items = self._asdict().items()
            l = len(items)
            with p.group(4, '%s([' % name, '])'):
                if breaking:
                    p.breakable()
                for i, (field, value) in enumerate(items):
                    p.text('%s: ' % field)
                    p.pretty(value)
                    if i < l - 1:
                        p.text(', ')
                        if breaking:
                            p.breakable()
    namedtuple_cls.__pretty__ = func


prettify_namedtuple(IngredientProperties, False)
prettify_namedtuple(Ingredient, False)
prettify_namedtuple(Recipe)


class Singleton(object):
    def __new__(type, *args):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance

    def __init__(self, name, doc=''):
        self.name = name
        self.__doc__ = doc

    def __repr__(self):
        return '<%s object>' % self.name


unknown = Singleton('unknown', '''a singleton used to show that the current
state of an ingredient (if it is dry or liquid) is unknown''')


undefined = Singleton(
    'undefined',
    'a singleton used to show if a specific property of a recipe is undefined')


class Ingredients(list):
    @property
    def top(self):
        return list.__getitem__(self, -1)

    def __contains__(self, ingredient_name):
        for ingredient in self:
            if ingredient.name == ingredient_name:
                return True
        return False

    def __getitem__(self, ingredient_name):
        for ingredient in self:
            if ingredient.name == ingredient_name:
                return ingredient
        raise KeyError(ingredient_name)

    def __setitem__(self, ingredient_name, ingredient_properties):
        for index, ingredient in enumerate(self):
            if ingredient.name == ingredient_name:
                # TODO: (remove the current value which is linked to
                # `ingredient_name`) and append the new value to the
                # mixing bowl!
                list.__setitem__(
                    self,
                    index,
                    Ingredient(ingredient_name, ingredient_properties))
                return
        self.append(Ingredient(ingredient_name, ingredient_properties))

    # TODO: probably needs a good doc-string :P
    def stir(self, n):
        l = len(self)
        self.insert(0 if n >= l else l - n - 1, self.pop())
