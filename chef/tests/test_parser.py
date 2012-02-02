from __future__ import with_statement

import re
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import pytest

from chef.datastructures import Ingredient, IngredientProperties, Ingredients,\
        unknown, undefined
from chef.errors.syntax import ChefSyntaxError, MissingEmptyLineError,\
        InvalidOvenTemperature, OrdinalIdentifierError,\
        InvalidCookingTimeError, InvalidCommandError,\
        InvalidTimeDeclarationError
import chef.parser as chef_parser


class TestMeasurePattern(object):
    params = {
        'test_dry_measure': [
            {'dry_measure': 'g'},
            {'dry_measure': 'kg'},
            {'dry_measure': 'pinch'},
            {'dry_measure': 'pinches'}],
        'test_liquid_measure': [
            {'liquid_measure': 'l'},
            {'liquid_measure': 'ml'},
            {'liquid_measure': 'dash'},
            {'liquid_measure': 'dashes'}],
        'test_dry_or_liquid_measure': [
            {'dry_or_liquid_measure': 'cup'},
            {'dry_or_liquid_measure': 'cups'},
            {'dry_or_liquid_measure': 'teaspoon'},
            {'dry_or_liquid_measure': 'teaspoons'},
            {'dry_or_liquid_measure': 'tablespoon'},
            {'dry_or_liquid_measure': 'tablespoons'}],
        'test_measure_type': [
            {'measure_type': 'heaped'},
            {'measure_type': 'level'}],
    }

    def test_dry_measure(self, dry_measure):
        m = re.match(chef_parser.DRY_MEASURE_PATTERN, dry_measure)
        assert m is not None
        assert m.group() == dry_measure

    def test_liquid_measure(self, liquid_measure):
        m = re.match(chef_parser.LIQUID_MEASURE_PATTERN, liquid_measure)
        assert m is not None
        assert m.group() == liquid_measure

    def test_dry_or_liquid_measure(self, dry_or_liquid_measure):
        m = re.match(
            chef_parser.DRY_OR_LIQUID_MEASURE_PATTERN, dry_or_liquid_measure)
        assert m is not None
        assert m.group() == dry_or_liquid_measure

    def test_measure_type(self, measure_type):
        m = re.match(chef_parser.MEASURE_TYPE_PATTERN, measure_type)
        assert m is not None
        assert m.group() == measure_type


class TestIngredientListItemPattern(object):
    params = {
        'test_measure_less': [
            {'item': '32 zucchinis'},
            {'item': '1 heaped water'},
            {'item': '7 levels lava'}]}

    def test_ingredient_name_only(self):
        m = re.match(chef_parser.INGREDIENT_LIST_ITEM_PATTERN, 'orange juice')
        assert m is not None
        assert m.groupdict() == {
            'initial_value': None,
            'measure_type': None,
            'measure': None,
            'name': 'orange juice'}

    def test_gramm(self):
        m = re.match(chef_parser.INGREDIENT_LIST_ITEM_PATTERN, '108 g lard')
        assert m is not None
        assert m.groupdict() == {
            'initial_value': '108',
            'measure_type': None,
            'measure': 'g',
            'name': 'lard'}

    def test_kilogramm(self):
        m = re.match(chef_parser.INGREDIENT_LIST_ITEM_PATTERN, '1 kg flour')
        assert m is not None
        assert m.groupdict() == {
            'initial_value': '1',
            'measure_type': None,
            'measure': 'kg',
            'name': 'flour'}

    def test_pinch(self):
        m = re.match(chef_parser.INGREDIENT_LIST_ITEM_PATTERN, '1 pinch salt')
        assert m is not None
        assert m.groupdict() == {
            'initial_value': '1',
            'measure_type': None,
            'measure': 'pinch',
            'name': 'salt'}

    def test_pinches(self):
        m = re.match(
            chef_parser.INGREDIENT_LIST_ITEM_PATTERN, '2 pinches sugar')
        assert m is not None
        assert m.groupdict() == {
            'initial_value': '2',
            'measure_type': None,
            'measure': 'pinches',
            'name': 'sugar'}

    def test_liter(self):
        m = re.match(chef_parser.INGREDIENT_LIST_ITEM_PATTERN, '5 l oil')
        assert m is not None
        assert m.groupdict() == {
            'initial_value': '5',
            'measure_type': None,
            'measure': 'l',
            'name': 'oil'}

    def test_milliliter(self):
        m = re.match(chef_parser.INGREDIENT_LIST_ITEM_PATTERN, '119 ml water')
        assert m is not None
        assert m.groupdict() == {
            'initial_value': '119',
            'measure_type': None,
            'measure': 'ml',
            'name': 'water'}

    def test_dash(self):
        m = re.match(
            chef_parser.INGREDIENT_LIST_ITEM_PATTERN, '1 dash tabasco')
        assert m is not None
        assert m.groupdict() == {
            'initial_value': '1',
            'measure_type': None,
            'measure': 'dash',
            'name': 'tabasco'}

    def test_dashes(self):
        m = re.match(
            chef_parser.INGREDIENT_LIST_ITEM_PATTERN, '3 dashes red wine')
        assert m is not None
        assert m.groupdict() == {
            'initial_value': '3',
            'measure_type': None,
            'measure': 'dashes',
            'name': 'red wine'}

    def test_cup(self):
        m = re.match(chef_parser.INGREDIENT_LIST_ITEM_PATTERN, '1 cup rice')
        assert m is not None
        assert m.groupdict() == {
            'initial_value': '1',
            'measure_type': None,
            'measure': 'cup',
            'name': 'rice'}

    def test_cups(self):
        m = re.match(chef_parser.INGREDIENT_LIST_ITEM_PATTERN, '111 cups oil')
        assert m is not None
        assert m.groupdict() == {
            'initial_value': '111',
            'measure_type': None,
            'measure': 'cups',
            'name': 'oil'}

    def test_teaspoon(self):
        m = re.match(
            chef_parser.INGREDIENT_LIST_ITEM_PATTERN, '1 teaspoon sugar')
        assert m is not None
        assert m.groupdict() == {
            'initial_value': '1',
            'measure_type': None,
            'measure': 'teaspoon',
            'name': 'sugar'}

    def test_teaspoons(self):
        m = re.match(
            chef_parser.INGREDIENT_LIST_ITEM_PATTERN, '1337 teaspoons beer')
        assert m is not None
        assert m.groupdict() == {
            'initial_value': '1337',
            'measure_type': None,
            'measure': 'teaspoons',
            'name': 'beer'}

    def test_tablespoon(self):
        m = re.match(
            chef_parser.INGREDIENT_LIST_ITEM_PATTERN, '1 tablespoon cocoa')
        assert m is not None
        assert m.groupdict() == {
            'initial_value': '1',
            'measure_type': None,
            'measure': 'tablespoon',
            'name': 'cocoa'}

    def test_tablespoons(self):
        m = re.match(
            chef_parser.INGREDIENT_LIST_ITEM_PATTERN, '4 tablespoons milk')
        assert m is not None
        assert m.groupdict() == {
            'initial_value': '4',
            'measure_type': None,
            'measure': 'tablespoons',
            'name': 'milk'}

    def test_measure_less(self, item):
        initial_value, name = item.split(' ', 1)
        m = re.match(chef_parser.INGREDIENT_LIST_ITEM_PATTERN, item)
        assert m is not None
        assert m.groupdict() == {
            'initial_value': initial_value,
            'measure_type': None,
            'measure': None,
            'name': name}

    def test_with_measure_type_heaped(self):
        m = re.match(
            chef_parser.INGREDIENT_LIST_ITEM_PATTERN,
            '6 heaped tablespoons cough syrup')
        assert m is not None
        assert m.groupdict() == {
            'initial_value': '6',
            'measure_type': 'heaped',
            'measure': 'tablespoons',
            'name': 'cough syrup'}

    def test_with_measure_type_level(self):
        m = re.match(
            chef_parser.INGREDIENT_LIST_ITEM_PATTERN,
            '1 level teaspoon coffee powder')
        assert m is not None
        assert m.groupdict() == {
            'initial_value': '1',
            'measure_type': 'level',
            'measure': 'teaspoon',
            'name': 'coffee powder'}

    def test_name_only(self):
        m = re.match(chef_parser.INGREDIENT_LIST_ITEM_PATTERN, 'apple')
        assert m is not None
        assert m.groupdict() == {
            'initial_value': None,
            'measure_type': None,
            'measure': None,
            'name': 'apple'}


class TestCookingTimePattern(object):
    s = 'Cooking time: '

    def test_hour(self):
        m = re.match(chef_parser.COOKING_TIME_PATTERN, self.s + '1 hour.')
        assert m is not None
        assert m.groupdict() == {
            'cooking_time': '1',
            'unit': 'hour'}

    def test_hours(self):
        m = re.match(chef_parser.COOKING_TIME_PATTERN, self.s + '3 hours.')
        assert m is not None
        assert m.groupdict() == {
            'cooking_time': '3',
            'unit': 'hours'}

    def test_minute(self):
        m = re.match(chef_parser.COOKING_TIME_PATTERN, self.s + '1 minute.')
        assert m is not None
        assert m.groupdict() == {
            'cooking_time': '1',
            'unit': 'minute'}

    def test_minutes(self):
        m = re.match(chef_parser.COOKING_TIME_PATTERN, self.s + '45 minutes.')
        assert m is not None
        assert m.groupdict() == {
            'cooking_time': '45',
            'unit': 'minutes'}


class TestOvenTemperaturePattern(object):
    s = 'Pre-heat oven to '

    def test_temperature_only(self):
        m = re.match(
            chef_parser.OVEN_TEMPERATURE_PATTERN,
            self.s + '110 degrees Celsius.')
        assert m is not None
        assert m.groupdict() == {'temperature': '110', 'gas_mark': None}

    def test_with_gas_mark(self):
        m = re.match(
            chef_parser.OVEN_TEMPERATURE_PATTERN,
            self.s + '110 degrees Celsius (gas mark 4).')
        assert m is not None
        assert m.groupdict() == {'temperature': '110', 'gas_mark': '4'}


class TestParseOrdinalIdentifier(object):
    params = {'test_invalid': [{'id': '42'}, {'id': 'first'}]}

    def test_invalid(self, id):
        with pytest.raises(OrdinalIdentifierError):
            chef_parser.parse_ordinal_identifier(id)

    def test_first(self):
        assert chef_parser.parse_ordinal_identifier('1st') == 1
        assert chef_parser.parse_ordinal_identifier('21st') == 21

    def test_second(self):
        assert chef_parser.parse_ordinal_identifier('2nd') == 2
        assert chef_parser.parse_ordinal_identifier('32nd') == 32

    def test_third(self):
        assert chef_parser.parse_ordinal_identifier('3rd') == 3
        assert chef_parser.parse_ordinal_identifier('73rd') == 73

    def test_nth(self):
        assert chef_parser.parse_ordinal_identifier('4th') == 4
        assert chef_parser.parse_ordinal_identifier('11th') == 11
        assert chef_parser.parse_ordinal_identifier('12th') == 12
        assert chef_parser.parse_ordinal_identifier('13th') == 13
        assert chef_parser.parse_ordinal_identifier('58th') == 58


class TestDetectIngredientState(object):
    params = {
        'test_dry': [
            {'measure': 'g'},
            {'measure': 'kg'},
            {'measure': 'pinch'},
            {'measure': 'pinches'}],
        'test_liquid': [
            {'measure': 'ml'},
            {'measure': 'l'},
            {'measure': 'dash'},
            {'measure': 'dashes'}],
        'test_unknown': [
            {'measure': 'cup'},
            {'measure': 'cups'},
            {'measure': 'teaspoon'},
            {'measure': 'teaspoons'},
            {'measure': 'tablespoon'},
            {'measure': 'tablespoons'}],
        'test_with_measure_type': [
            {'measure': 'pinch', 'measure_type': 'heaped'},
            {'measure': 'pinches', 'measure_type': 'heaped'},
            {'measure': 'cup', 'measure_type': 'heaped'},
            {'measure': 'cups', 'measure_type': 'heaped'},
            {'measure': 'teaspoon', 'measure_type': 'heaped'},
            {'measure': 'teaspoons', 'measure_type': 'heaped'},
            {'measure': 'tablespoon', 'measure_type': 'heaped'},
            {'measure': 'tablespoons', 'measure_type': 'heaped'},
            {'measure': 'pinch', 'measure_type': 'level'},
            {'measure': 'pinches', 'measure_type': 'level'},
            {'measure': 'cup', 'measure_type': 'level'},
            {'measure': 'cups', 'measure_type': 'level'},
            {'measure': 'teaspoon', 'measure_type': 'level'},
            {'measure': 'teaspoons', 'measure_type': 'level'},
            {'measure': 'tablespoon', 'measure_type': 'level'},
            {'measure': 'tablespoons', 'measure_type': 'level'}]}

    def test_measure_less(self):
        is_dry, is_liquid = chef_parser.detect_ingredient_state(None)
        assert not is_dry
        assert not is_liquid

    def test_dry(self, measure):
        is_dry, is_liquid = chef_parser.detect_ingredient_state(measure)
        assert is_dry
        assert not is_liquid

    def test_liquid(self, measure):
        is_dry, is_liquid = chef_parser.detect_ingredient_state(measure)
        assert not is_dry
        assert is_liquid

    def test_unknown(self, measure):
        is_dry, is_liquid = chef_parser.detect_ingredient_state(measure)
        assert is_dry is unknown
        assert is_liquid is unknown

    def test_with_measure_type(self, measure, measure_type):
        is_dry, is_liquid = chef_parser.detect_ingredient_state(
            measure, measure_type)
        assert is_dry
        assert not is_liquid

    def test_invalid(self):
        with pytest.raises(ValueError) as e:
            chef_parser.detect_ingredient_state('blah')
        assert e.value.message == "invalid measure: 'blah'"


class TestParseIngredientList(object):
    params = {'test_nonmatching_measure': [
        {'line': '5 tablespoon brown sugar\n'},
        {'line': '1 cups milk'},
        # ....
        ]}

    def test_no_items(self):
        ingredients, lineno = chef_parser.parse_ingredient_list('', 4)
        assert ingredients == Ingredients()
        assert lineno == 4

    def test_one_item(self):
        ingredients, lineno = chef_parser.parse_ingredient_list(
            '111 cups oil\n', 4)
        assert ingredients == Ingredients([
            Ingredient('oil', IngredientProperties(111, unknown, unknown))])
        assert lineno == 5

    def test_multiple_items(self):
        ingredients, lineno = chef_parser.parse_ingredient_list(
            '111 cups oil\n75 heaped tablespoons sugar\neggs\n', 4)
        assert ingredients == Ingredients([
            Ingredient('oil', IngredientProperties(111, unknown, unknown)),
            Ingredient('sugar', IngredientProperties(75, unknown, unknown)),
            Ingredient('eggs', IngredientProperties(None, False, False))])
        assert lineno == 7

    def test_misc(self):
        ingredient_list = '''72 kg tuna
2300 g lettuce
37 cups olive oil
18 peppers
'''
        ingredients, lineno = chef_parser.parse_ingredient_list(
            ingredient_list, 4)
        assert ingredients == Ingredients([
            Ingredient('tuna', IngredientProperties(72, True, False)),
            Ingredient('lettuce', IngredientProperties(2300, True, False)),
            Ingredient(
                'olive oil', IngredientProperties(37, unknown, unknown)),
            Ingredient('peppers', IngredientProperties(18, False, False))])
        assert lineno == 8

    def test_multiple_definition_of_same_name(self):
        # the website says: "If an ingredient is repeated, the new value is
        # used and previous values for that ingredient are ignored."
        ingredients, lineno = chef_parser.parse_ingredient_list(
            '111 cups oil\n75 cups oil\n', 4)
        assert len(ingredients) == 1
        assert ingredients == [
            Ingredient('oil', IngredientProperties(75, unknown, unknown))]
        assert lineno == 6

    def test_nonmatching_measure(self, line):
        ingredients, lineno = chef_parser.parse_ingredient_list(line, 4)


class TestParseCookingTime(object):
    s = 'Cooking time: '

    def test_hour(self):
        parsed_cooking_time = chef_parser.parse_cooking_time(
            self.s + '1 hour.')
        assert chef_parser.is_cooking_time(self.s + '1 hour.')
        assert parsed_cooking_time == (1, 'hour')

    def test_hours(self):
        parsed_cooking_time = chef_parser.parse_cooking_time(
            self.s + '3 hours.')
        assert chef_parser.is_cooking_time(self.s + '3 hours.')
        assert parsed_cooking_time == (3, 'hours')

    def test_minute(self):
        parsed_cooking_time = chef_parser.parse_cooking_time(
            self.s + '1 minute.')
        assert chef_parser.is_cooking_time(self.s + '1 minute.')
        assert parsed_cooking_time == (1, 'minute')

    def test_minutes(self):
        parsed_cooking_time = chef_parser.parse_cooking_time(
            self.s + '20 minutes.')
        assert chef_parser.is_cooking_time(self.s + '20 minutes.')
        assert parsed_cooking_time == (20, 'minutes')

    def test_invalid(self):
        with pytest.raises(InvalidCookingTimeError):
            chef_parser.parse_cooking_time(self.s + 'meh.')


class TestParseOvenTemperature(object):
    s = 'Pre-heat oven to '

    def test_temperature_only(self):
        parsed_oven_temperature = chef_parser.parse_oven_temperature(
            self.s + '220 degrees Celsius.')
        assert parsed_oven_temperature == (220, None)

    def test_with_gas_mark(self):
        parsed_oven_temperature = chef_parser.parse_oven_temperature(
            self.s + '220 degrees Celsius (gas mark 4).')
        assert parsed_oven_temperature == (220, 4)

    def test_invalid(self):
        with pytest.raises(InvalidOvenTemperature):
            chef_parser.parse_oven_temperature('200 degrees.')


class TestGetOrdinalID(object):
    pattern = re.compile(
        'Put tomatoes into (?:(%s )|the )salad bowl\.' % (
            chef_parser.ORDINAL_IDENTIFIER_PATTERN))

    def test_without_id(self):
        m = re.match(self.pattern, 'Put tomatoes into the salad bowl.')
        id_ = chef_parser.get_ordinal_id(m, 1)
        assert id_ is None

    def test_with_id(self):
        m = re.match(self.pattern, 'Put tomatoes into 3rd salad bowl.')
        id_ = chef_parser.get_ordinal_id(m, 1)
        assert id_ == 3


class TestParseIngredientPrepositionNthMixingBowl(object):
    def test_with_ordinal_id(self):
        d = chef_parser.parse_ingredient_preposition_nth_mixing_bowl(
            'Fold', 'into', 'tomatoes into 2nd mixing bowl.')
        assert d == {
            'command': 'fold',
            'ingredient': 'tomatoes',
            'mixing_bowl_id': 2}

    def test_without_ordinal_id(self):
        d = chef_parser.parse_ingredient_preposition_nth_mixing_bowl(
            'Put', 'into', 'eggs into mixing bowl.')
        assert d == {
            'command': 'put',
            'ingredient': 'eggs',
            'mixing_bowl_id': None}

    def test_invalid(self):
        with pytest.raises(ChefSyntaxError):
            chef_parser.parse_ingredient_preposition_nth_mixing_bowl(
                'Blub', 'into', 'gnagnagna!')


class TestParseIngredientOptionalPrepositionNthMixingBowl(object):
    def test_with_ordinal_id(self):
        d = chef_parser.parse_ingredient_optional_preposition_nth_mixing_bowl(
            'Add', 'to', 'meat balls to 4th mixing bowl.')
        assert d == {
            'command': 'add',
            'ingredient': 'meat balls',
            'mixing_bowl_id': 4}

    def test_without_ordinal_id(self):
        d = chef_parser.parse_ingredient_optional_preposition_nth_mixing_bowl(
            'Add', 'to', 'potatoes to mixing bowl.')
        assert d == {
            'command': 'add',
            'ingredient': 'potatoes',
            'mixing_bowl_id': None}

    def test_short(self):
        d = chef_parser.parse_ingredient_optional_preposition_nth_mixing_bowl(
            'Add', 'to', 'eggs.')
        assert d == {
            'command': 'add',
            'ingredient': 'eggs',
            'mixing_bowl_id': None}

    def test_invalid(self):
        with pytest.raises(ChefSyntaxError):
            chef_parser.parse_ingredient_optional_preposition_nth_mixing_bowl(
                'Flush', 'to', 'hibble-dibble!')


class TestParseTake(object):
    def test_valid(self):
        d = chef_parser.parse_take('eggs from refrigerator.')
        assert d == {'command': 'take', 'ingredient': 'eggs'}

    def test_invalid(self):
        with pytest.raises(InvalidCommandError):
            chef_parser.parse_take('potatoes.')


class TestParsePut(object):
    params = {
        'test_invalid': [
            {'invalid_code': 'meat into the 5th mixing bowl.'},
            {'invalid_code': 'meat into the mixing bowl.'}]}

    def test_general(self):
        d = chef_parser.parse_put('salt into mixing bowl.')
        assert d == {
            'command': 'put', 'ingredient': 'salt', 'mixing_bowl_id': None}

    def test_with_mixing_bowl(self):
        d = chef_parser.parse_put('sugar into 5th mixing bowl.')
        assert d == {
            'command': 'put', 'ingredient': 'sugar', 'mixing_bowl_id': 5}

    def test_invalid(self, invalid_code):
        with pytest.raises(InvalidCommandError) as e:
            chef_parser.parse_put(invalid_code)
        assert e.value.cmd == 'Put'


class TestParseFold(object):
    params = {
        'test_invalid': [
            {'invalid_code': 'cheese into the 13th mixing bowl.'},
            {'invalid_code': 'pudding into the mixing bowl.'}]}

    def test_general(self):
        d = chef_parser.parse_fold('sausage into mixing bowl.')
        assert d == {
            'command': 'fold', 'ingredient': 'sausage', 'mixing_bowl_id': None}

    def test_with_mixing_bowl(self):
        d = chef_parser.parse_fold('mustard into 6th mixing bowl.')
        assert d == {
            'command': 'fold', 'ingredient': 'mustard', 'mixing_bowl_id': 6}

    def test_invalid(self, invalid_code):
        with pytest.raises(InvalidCommandError) as e:
            chef_parser.parse_fold(invalid_code)
        assert e.value.cmd == 'Fold'


class TestParseAdd(object):
    def test_general(self):
        d = chef_parser.parse_add('flour.')
        assert d == {
            'command': 'add',
            'ingredient': 'flour',
            'mixing_bowl_id': None}

    def test_with_mixing_bowl(self):
        d = chef_parser.parse_add('ketchup to 3rd mixing bowl.')
        assert d == {
            'command': 'add', 'ingredient': 'ketchup', 'mixing_bowl_id': 3}

    def test_unusual(self):
        # be aware of the word "the" in all the test_unusual methods in this
        # module!
        d = chef_parser.parse_add('cream to the 5th mixing bowl.')
        assert d == {
            'command': 'add',
            'ingredient': 'cream to the 5th mixing bowl',
            'mixing_bowl_id': None}
        d = chef_parser.parse_add('salad to the mixing bowl.')
        assert d == {
            'command': 'add',
            'ingredient': 'salad to the mixing bowl',
            'mixing_bowl_id': None}


class TestParseRemove(object):
    def test_general(self):
        d = chef_parser.parse_remove('red wine.')
        assert d == {
            'command': 'remove',
            'ingredient': 'red wine',
            'mixing_bowl_id': None}

    def test_with_mixing_bowl(self):
        d = chef_parser.parse_remove('fish from 6th mixing bowl.')
        assert d == {
            'command': 'remove', 'ingredient': 'fish', 'mixing_bowl_id': 6}

    def test_unusual(self):
        d = chef_parser.parse_remove('baking powder from the 5th mixing bowl.')
        assert d == {
            'command': 'remove',
            'ingredient': 'baking powder from the 5th mixing bowl',
            'mixing_bowl_id': None}
        d = chef_parser.parse_remove('vanilla sugar from the mixing bowl.')
        assert d == {
            'command': 'remove',
            'ingredient': 'vanilla sugar from the mixing bowl',
            'mixing_bowl_id': None}


class TestParseCombine(object):
    def test_general(self):
        d = chef_parser.parse_combine('tomatoes.')
        assert d == {
            'command': 'combine',
            'ingredient': 'tomatoes',
            'mixing_bowl_id': None}

    def test_with_mixing_bowl(self):
        d = chef_parser.parse_combine('pickles into 3rd mixing bowl.')
        assert d == {
            'command': 'combine', 'ingredient': 'pickles', 'mixing_bowl_id': 3}

    def test_unusual(self):
        d = chef_parser.parse_combine('marzipan into the 2nd mixing bowl.')
        assert d == {
            'command': 'combine',
            'ingredient': 'marzipan into the 2nd mixing bowl',
            'mixing_bowl_id': None}
        d = chef_parser.parse_combine('onions into the mixing bowl.')
        assert d == {
            'command': 'combine',
            'ingredient': 'onions into the mixing bowl',
            'mixing_bowl_id': None}


class TestParseDivide(object):
    def test_general(self):
        d = chef_parser.parse_divide('chocolate.')
        assert d == {
            'command': 'divide',
            'ingredient': 'chocolate',
            'mixing_bowl_id': None}

    def test_with_mixing_bowl(self):
        d = chef_parser.parse_divide('cheese into 7th mixing bowl.')
        assert d == {
            'command': 'divide', 'ingredient': 'cheese', 'mixing_bowl_id': 7}

    def test_unusual(self):
        d = chef_parser.parse_divide('peppercorns into the 1st mixing bowl.')
        assert d == {
            'command': 'divide',
            'ingredient': 'peppercorns into the 1st mixing bowl',
            'mixing_bowl_id': None}
        d = chef_parser.parse_divide('parsley into the mixing bowl.')
        assert d == {
            'command': 'divide',
            'ingredient': 'parsley into the mixing bowl',
            'mixing_bowl_id': None}


class TestParseAddDry(object):
    def test_general(self):
        d = chef_parser.parse_add_dry('dry ingredients.')
        assert d == {'command': 'add_dry', 'mixing_bowl_id': None}

    def test_with_specific_mixing_bowl(self):
        d = chef_parser.parse_add_dry(
            'dry ingredients to 2nd mixing bowl.')
        assert d == {'command': 'add_dry', 'mixing_bowl_id': 2}

    def test_invalid(self):
        with pytest.raises(InvalidCommandError):
            chef_parser.parse_add_dry('dry ingredients to the mixing bowl.')


def test_parse_liquefy():
    d = chef_parser.parse_liquefy_ingredient('melted butter.')
    assert d == {
        'command': 'liquefy_ingredient', 'ingredient': 'melted butter'}


class TestParseLiquefyContents(object):
    def test_general(self):
        d = chef_parser.parse_liquefy_contents('contents of the mixing bowl.')
        assert d == {'command': 'liquefy_contents', 'mixing_bowl_id': None}

    def test_specific_mixing_bowl(self):
        d = chef_parser.parse_liquefy_contents(
            'contents of the 4th mixing bowl.')
        assert d == {'command': 'liquefy_contents', 'mixing_bowl_id': 4}

    def test_unusual(self):
        # looks like a "liquefy contents" command, but it isn't!
        d = chef_parser.parse_liquefy_contents('contents of 3rd mixing bowl.')
        assert d == {
            'command': 'liquefy_ingredient',
            'ingredient': 'contents of 3rd mixing bowl'}


class TestParseStirMinutes(object):
    def test_general(self):
        d = chef_parser.parse_stir('for 5 minutes.')
        assert d == {
            'command': 'stir_minutes',
            'mixing_bowl_id': None,
            'minutes': 5}

    def test_with_mixing_bowl(self):
        d = chef_parser.parse_stir('the mixing bowl for 3 minutes.')
        assert d == {
            'command': 'stir_minutes', 'minutes': 3, 'mixing_bowl_id': None}

    def test_with_specific_mixing_bowl(self):
        d = chef_parser.parse_stir('the 4th mixing bowl for 10 minutes.')
        assert d == {
            'command': 'stir_minutes', 'minutes': 10, 'mixing_bowl_id': 4}

    def test_invalid(self):
        with pytest.raises(InvalidCommandError):
            chef_parser.parse_stir('the mixing bowl.')


class TestParseStirIngredient(object):
    def test_general(self):
        d = chef_parser.parse_stir('apples into the mixing bowl.')
        assert d == {
            'command': 'stir_ingredient',
            'ingredient': 'apples',
            'mixing_bowl_id': None}

    def test_with_specific_mixing_bowl(self):
        d = chef_parser.parse_stir('milk into the 2nd mixing bowl.')
        assert d == {
            'command': 'stir_ingredient',
            'ingredient': 'milk',
            'mixing_bowl_id': 2}

    def test_invalid(self):
        with pytest.raises(InvalidCommandError):
            chef_parser.parse_stir('vodka into 5th mixing bowl.')


class TestParseMix(object):
    params = {'test_invalid': [
        {'invalid_code': '5th mixing bowl well.'},
        {'invalid_code': 'the mixing bowl.'}]}

    def test_general(self):
        d = chef_parser.parse_mix('well.')
        assert d == {'command': 'mix', 'mixing_bowl_id': None}

    def test_with_mixing_bowl(self):
        d = chef_parser.parse_mix('the mixing bowl well.')
        assert d == {'command': 'mix', 'mixing_bowl_id': None}

    def test_with_specific_mixing_bowl(self):
        d = chef_parser.parse_mix('the 3rd mixing bowl well.')
        assert d == {'command': 'mix', 'mixing_bowl_id': 3}

    def test_invalid(self, invalid_code):
        with pytest.raises(InvalidCommandError):
            chef_parser.parse_mix(invalid_code)


class TestParseClean(object):
    def test_general(self):
        d = chef_parser.parse_clean('mixing bowl.')
        assert d == {'command': 'clean', 'mixing_bowl_id': None}

    def test_with_specific_mixing_bowl(self):
        d = chef_parser.parse_clean('3rd mixing bowl.')
        assert d == {'command': 'clean', 'mixing_bowl_id': 3}

    def test_invalid(self):
        with pytest.raises(InvalidCommandError):
            chef_parser.parse_clean('the mixing bowl.')


class TestParsePour(object):
    def test_general(self):
        d = chef_parser.parse_pour(
            'contents of the mixing bowl into the baking dish.')
        assert d == {
            'command': 'pour',
            'mixing_bowl_id': None,
            'baking_dish_id': None}

    def test_with_mixing_bowl(self):
        d = chef_parser.parse_pour(
            'contents of the 2nd mixing bowl into the baking dish.')
        assert d == {
            'command': 'pour',
            'mixing_bowl_id': 2,
            'baking_dish_id': None}

    def test_with_baking_dish(self):
        d = chef_parser.parse_pour(
            'contents of the mixing bowl into the 3rd baking dish.')
        assert d == {
            'command': 'pour',
            'mixing_bowl_id': None,
            'baking_dish_id': 3}

    def test_with_both(self):
        d = chef_parser.parse_pour(
            'contents of the 4th mixing bowl into the 6th baking dish.')
        assert d == {
            'command': 'pour',
            'mixing_bowl_id': 4,
            'baking_dish_id': 6}

    def test_invalid(self):
        with pytest.raises(InvalidCommandError):
            # leaving out "the"
            chef_parser.parse_pour('contents of mixing bowl into baking dish.')


class TestParseRefrigerate(object):
    def test_general(self):
        d = chef_parser.parse_refrigerate('.')
        assert d == {'command': 'refrigerate', 'hours': None}

    def test_with_hour(self):
        d = chef_parser.parse_refrigerate('for 1 hour.')
        assert d == {'command': 'refrigerate', 'hours': 1}

    def test_with_hours(self):
        d = chef_parser.parse_refrigerate('for 3 hours.')
        assert d == {'command': 'refrigerate', 'hours': 3}

    def test_invalid(self):
        with pytest.raises(InvalidCommandError):
            chef_parser.parse_refrigerate('for 5 minutes.')

    def test_invalid_time_declaration(self):
        with pytest.raises(InvalidTimeDeclarationError):
            chef_parser.parse_refrigerate('for 1 hours.')
        with pytest.raises(InvalidTimeDeclarationError):
            chef_parser.parse_refrigerate('for 2 hour.')


class TestParseLoopStart(object):
    def test_valid(self):
        d = chef_parser.parse_loop_start('Eat', 'the burger.')
        assert d == {
            'command': 'loop_start', 'verb': 'Eat', 'ingredient': 'burger'}

    def test_invalid(self):
        with pytest.raises(InvalidCommandError):
            chef_parser.parse_loop_start('Shake', 'it.')


class TestParseLoopEnd(object):
    def test_without_ingredient(self):
        d = chef_parser.parse_loop_end('Bake', 'until heated.')
        assert d == {
            'command': 'loop_end', 'verb': 'heated', 'ingredient': None}

    def test_with_ingredient(self):
        # I apologize in advance to all vegetarians who are insulted by the
        # following lines
        d = chef_parser.parse_loop_end('Punch', 'the broccoli until killed.')
        assert d == {
            'command': 'loop_end', 'verb': 'killed', 'ingredient': 'broccoli'}

    def test_invalid(self):
        with pytest.raises(InvalidCommandError):
            chef_parser.parse_loop_end('Throw', 'meat balls until gone.')


class TestParseMethod(object):
    def test_single_instruction(self):
        parsed_instructions, lineno = chef_parser.parse_method(
            'Method.\nAdd flour to 3rd mixing bowl.', 1)
        assert lineno == 2
        assert len(parsed_instructions) == 1
        assert parsed_instructions == [{
            'command': 'add',
            'ingredient': 'flour',
            'mixing_bowl_id': 3,
            'lineno': 2}]

    def test_multiple_instructions(self):
        parsed_instructions, lineno = chef_parser.parse_method(
            'Method.\n'
            'Add flour to 3rd mixing bowl.\n'
            'Take sugar from refrigerator.', 1)
        assert lineno == 3
        assert len(parsed_instructions) == 2
        assert parsed_instructions == [
            {
                'command': 'add',
                'ingredient': 'flour',
                'mixing_bowl_id': 3,
                'lineno': 2},
            {
                'command': 'take',
                'ingredient': 'sugar',
                'lineno': 3}]


def test_parse_serves():
    num_of_diners = chef_parser.parse_serves('Serves 7.', 12)
    assert num_of_diners == 7


class TestParseRecipe(object):
    def test_missing_first_blank_line(self):
        with pytest.raises(MissingEmptyLineError) as e:
            chef_parser.parse_recipe(
                StringIO('The title.\nno line break here.'))
        assert e.value.lineno == 2

    def test_without_method(self, missing_method_recipe):
        with pytest.raises(ChefSyntaxError) as e:
            chef_parser.parse_recipe(missing_method_recipe)
        assert e.value.msg == 'missing syntax element: method'
        assert e.value.lineno == 5

    def test_multiple_instructions(self, multiple_instr):
        recipe = chef_parser.parse_recipe(multiple_instr)
        assert recipe.ingredients == []
        assert recipe.cooking_time is undefined
        assert recipe.oven_temperature is undefined
        assert recipe.instructions == [
            {
                'command': 'put',
                'ingredient': 'sugar',
                'mixing_bowl_id': None,
                'lineno': 4},
            {
                'command': 'liquefy_ingredient',
                'ingredient': 'sugar',
                'lineno': 5},
            {
                'command': 'pour',
                'mixing_bowl_id': None,
                'baking_dish_id': None,
                'lineno': 6}]
        assert recipe.serves is undefined

    def test_only_required_elements(self, only_title_and_method):
        recipe = chef_parser.parse_recipe(only_title_and_method)
        assert recipe.ingredients == []
        assert recipe.cooking_time is undefined
        assert recipe.oven_temperature is undefined
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 4}]
        assert recipe.serves is undefined

    def test_description_only(self, description_only):
        recipe = chef_parser.parse_recipe(description_only)
        assert recipe.ingredients == []
        assert recipe.cooking_time is undefined
        assert recipe.oven_temperature is undefined
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 10}]
        assert recipe.serves is undefined

    def test_ingredients_only(self, ingredients_only):
        recipe = chef_parser.parse_recipe(ingredients_only)
        assert recipe.ingredients == [
            Ingredient('lard', IngredientProperties(108, True, False)),
            Ingredient('oil', IngredientProperties(111, unknown, unknown))]
        assert recipe.cooking_time is undefined
        assert recipe.oven_temperature is undefined
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 8}]
        assert recipe.serves is undefined

    def test_cooking_time_only(self, cooking_time_only):
        recipe = chef_parser.parse_recipe(cooking_time_only)
        assert recipe.ingredients == []
        assert recipe.cooking_time == (20, 'minutes')
        assert recipe.oven_temperature is undefined
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 6}]
        assert recipe.serves is undefined

    def test_oven_temp_only(self, oven_temp_only):
        recipe = chef_parser.parse_recipe(oven_temp_only)
        assert recipe.ingredients == []
        assert recipe.cooking_time is undefined
        assert recipe.oven_temperature == (200, 5)
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 6}]
        assert recipe.serves is undefined

    def test_serves_only(self, serves_only):
        recipe = chef_parser.parse_recipe(serves_only)
        assert recipe.ingredients == []
        assert recipe.cooking_time is undefined
        assert recipe.oven_temperature is undefined
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 4}]
        assert recipe.serves == 4

    def test_description_and_ingredients(self, description_and_ingredients):
        recipe = chef_parser.parse_recipe(description_and_ingredients)
        assert recipe.ingredients == [
            Ingredient('gnocchi', IngredientProperties(1, True, False)),
            Ingredient('butter', IngredientProperties(2, unknown, unknown)),
            Ingredient('flour', IngredientProperties(1, unknown, unknown)),
            Ingredient('milk', IngredientProperties(1, unknown, unknown)),
            Ingredient('cheese', IngredientProperties(4, unknown, unknown))]
        assert recipe.cooking_time is undefined
        assert recipe.oven_temperature is undefined
        assert recipe.instructions == [
                {'command': 'take', 'ingredient': 'apple', 'lineno': 14}]
        assert recipe.serves is undefined

    def test_description_and_cooking_time(self, description_and_cooking_time):
        recipe = chef_parser.parse_recipe(description_and_cooking_time)
        assert recipe.ingredients == []
        assert recipe.cooking_time == (2, 'hours')
        assert recipe.oven_temperature is undefined
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 9}]
        assert recipe.serves is undefined

    def test_description_and_oven_temp(self, description_and_oven_temp):
        recipe = chef_parser.parse_recipe(description_and_oven_temp)
        assert recipe.ingredients == []
        assert recipe.cooking_time is undefined
        assert recipe.oven_temperature == (250, 7)
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 9}]
        assert recipe.serves is undefined

    def test_description_and_serves_recipe(self, description_and_serves):
        recipe = chef_parser.parse_recipe(description_and_serves)
        assert recipe.ingredients == []
        assert recipe.cooking_time is undefined
        assert recipe.oven_temperature is undefined
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 7}]
        assert recipe.serves == 5

    def test_ingredients_and_cooking_time(self, ingredients_and_cooking_time):
        recipe = chef_parser.parse_recipe(ingredients_and_cooking_time)
        assert recipe.ingredients == [
            Ingredient('tuna', IngredientProperties(72, True, False)),
            Ingredient('lettuce', IngredientProperties(2300, True, False)),
            Ingredient(
                'olive oil', IngredientProperties(37, unknown, unknown)),
            Ingredient('peppers', IngredientProperties(18, False, False))]
        assert recipe.cooking_time == (10, 'minutes')
        assert recipe.oven_temperature is undefined
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 12}]
        assert recipe.serves is undefined

    def test_ingredients_and_oven_temp(self, ingredients_and_oven_temp):
        recipe = chef_parser.parse_recipe(ingredients_and_oven_temp)
        assert recipe.ingredients == [
            Ingredient('marshmallows', IngredientProperties(1, True, False)),
            Ingredient('bananas', IngredientProperties(5, False, False)),
            Ingredient('hazelnuts', IngredientProperties(3, unknown, unknown)),
            Ingredient('chocolate', IngredientProperties(500, True, False))]
        assert recipe.cooking_time is undefined
        assert recipe.oven_temperature == (220, None)
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 12}]
        assert recipe.serves is undefined

    def test_ingredients_and_serves(self, ingredients_and_serves):
        recipe = chef_parser.parse_recipe(ingredients_and_serves)
        assert recipe.ingredients == [
            Ingredient('water', IngredientProperties(2, False, True)),
            Ingredient('raisins', IngredientProperties(13, False, False)),
            Ingredient('rum', IngredientProperties(6, False, True))]
        assert recipe.cooking_time is undefined
        assert recipe.oven_temperature is undefined
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 9}]
        assert recipe.serves == 23

    def test_cooking_time_and_oven_temp(self, cooking_time_and_oven_temp):
        recipe = chef_parser.parse_recipe(cooking_time_and_oven_temp)
        assert recipe.ingredients == []
        assert recipe.cooking_time == (45, 'minutes')
        assert recipe.oven_temperature == (250, 5)
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 8}]
        assert recipe.serves is undefined

    def test_cooking_time_and_serves(self, cooking_time_and_serves):
        recipe = chef_parser.parse_recipe(cooking_time_and_serves)
        assert recipe.ingredients == []
        assert recipe.cooking_time == (15, 'minutes')
        assert recipe.oven_temperature is undefined
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 6}]
        assert recipe.serves == 1

    def test_oven_temp_and_serves(self, oven_temp_and_serves):
        recipe = chef_parser.parse_recipe(oven_temp_and_serves)
        assert recipe.ingredients == []
        assert recipe.cooking_time is undefined
        assert recipe.oven_temperature == (175, None)
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 6}]
        assert recipe.serves == 8

    def test_descr_ingredients_and_cooking_time(self, descr_ingr_cooking_time):
        recipe = chef_parser.parse_recipe(descr_ingr_cooking_time)
        assert recipe.ingredients == [
            Ingredient('apple', IngredientProperties(None, False, False)),
            Ingredient('cinnamon', IngredientProperties(2, unknown, unknown)),
            Ingredient(
                'brown sugar', IngredientProperties(1, unknown, unknown))]
        assert recipe.cooking_time == (20, 'minutes')
        assert recipe.oven_temperature is undefined
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 13}]
        assert recipe.serves is undefined

    def test_descr_ingredients_and_oven_temp(self, descr_ingr_oven_temp):
        recipe = chef_parser.parse_recipe(descr_ingr_oven_temp)
        assert recipe.ingredients == [
            Ingredient('water', IngredientProperties(100, False, True)),
            Ingredient('oranges', IngredientProperties(3, False, False)),
            Ingredient('lemon juice', IngredientProperties(2, False, True)),
            Ingredient(
                'vanilla ice cream', IngredientProperties(250, False, True))]
        assert recipe.cooking_time is undefined
        assert recipe.oven_temperature == (250, None)
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 16}]
        assert recipe.serves is undefined

    def test_descr_ingredients_and_serves(self, descr_ingr_serves):
        recipe = chef_parser.parse_recipe(descr_ingr_serves)
        assert recipe.ingredients == [
            Ingredient('frog legs', IngredientProperties(7, False, False)),
            Ingredient('spiders', IngredientProperties(23, True, False)),
            Ingredient(
                'zombie brains', IngredientProperties(13, False, False)),
            Ingredient(
                'werewolf blood', IngredientProperties(200, False, True))]
        assert recipe.cooking_time is undefined
        assert recipe.oven_temperature is undefined
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 12}]
        assert recipe.serves == 12

    def test_descr_cooking_time_oven_temp(self, descr_cooking_time_oven_temp):
        recipe = chef_parser.parse_recipe(descr_cooking_time_oven_temp)
        assert recipe.ingredients == []
        assert recipe.cooking_time == (15, 'minutes')
        assert recipe.oven_temperature == (200, None)
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 10}]
        assert recipe.serves is undefined

    def test_descr_cooking_time_and_serves(self, descr_cooking_time_serves):
        recipe = chef_parser.parse_recipe(descr_cooking_time_serves)
        assert recipe.ingredients == []
        assert recipe.cooking_time == (7, 'hours')
        assert recipe.oven_temperature is undefined
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 8}]
        assert recipe.serves == 5

    def test_descr_oven_temp_and_serves(self, descr_oven_temp_serves):
        recipe = chef_parser.parse_recipe(descr_oven_temp_serves)
        assert recipe.ingredients == []
        assert recipe.cooking_time is undefined
        assert recipe.oven_temperature == (80, 2)
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 9}]
        assert recipe.serves == 1

    def test_ingr_cooking_time_oven_temp(self, ingr_cooking_time_oven_temp):
        recipe = chef_parser.parse_recipe(ingr_cooking_time_oven_temp)
        assert recipe.ingredients == [
            Ingredient('pickles', IngredientProperties(5, False, False)),
            Ingredient('wheat', IngredientProperties(200, True, False))]
        assert recipe.cooking_time == (25, 'minutes')
        assert recipe.oven_temperature == (220, None)
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 12}]
        assert recipe.serves is undefined

    def test_ingr_cooking_time_serves(self, ingr_cooking_time_serves):
        recipe = chef_parser.parse_recipe(ingr_cooking_time_serves)
        assert recipe.ingredients == [
            Ingredient('girls', IngredientProperties(2, False, False)),
            Ingredient('chocolate', IngredientProperties(1, unknown, unknown))]
        assert recipe.cooking_time == (1, 'minute')
        assert recipe.oven_temperature is undefined
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 10}]
        assert recipe.serves == 2

    def test_cooking_time_oven_temp_serves(self,
            cooking_time_oven_temp_serves):
        recipe = chef_parser.parse_recipe(cooking_time_oven_temp_serves)
        assert recipe.ingredients == []
        assert recipe.cooking_time == (2, 'hours')
        assert recipe.oven_temperature == (130, None)
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 8}]
        assert recipe.serves == 7

    def test_descr_ingr_cooking_time_oven_temp(self,
            descr_ingr_cooking_time_oven_temp):
        recipe = chef_parser.parse_recipe(descr_ingr_cooking_time_oven_temp)
        assert recipe.ingredients == [
            Ingredient('beer', IngredientProperties(25, False, True)),
            Ingredient('mustard', IngredientProperties(5, True, False))]
        assert recipe.cooking_time == (34, 'minutes')
        assert recipe.oven_temperature == (85, None)
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 14}]
        assert recipe.serves is undefined

    def test_descr_ingr_cooking_time_serves(self,
            descr_ingr_cooking_time_serves):
        recipe = chef_parser.parse_recipe(descr_ingr_cooking_time_serves)
        assert recipe.ingredients == [
            Ingredient('oil', IngredientProperties(2, False, True)),
            Ingredient('potatoes', IngredientProperties(4, True, False))]
        assert recipe.cooking_time == (3, 'hours')
        assert recipe.oven_temperature is undefined
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 13}]
        assert recipe.serves == 4

    def test_descr_ingr_oven_temp_serves(self, descr_ingr_oven_temp_serves):
        recipe = chef_parser.parse_recipe(descr_ingr_oven_temp_serves)
        assert recipe.ingredients == [
            Ingredient('water', IngredientProperties(1, False, True)),
            Ingredient('buns', IngredientProperties(6, False, False))]
        assert recipe.cooking_time is undefined
        assert recipe.oven_temperature == (120, None)
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 12}]
        assert recipe.serves == 6

    def test_descr_cooking_time_oven_temp_serves(self,
            descr_cooking_time_oven_temp_serves):
        recipe = chef_parser.parse_recipe(descr_cooking_time_oven_temp_serves)
        assert recipe.ingredients == []
        assert recipe.cooking_time == (17, 'minutes')
        assert recipe.oven_temperature == (220, 7)
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 10}]
        assert recipe.serves == 2

    def test_ingr_cooking_time_oven_temp_serves(self,
            ingr_cooking_time_oven_temp_serves):
        recipe = chef_parser.parse_recipe(ingr_cooking_time_oven_temp_serves)
        assert recipe.ingredients == [
            Ingredient('yoghurt', IngredientProperties(100, False, True)),
            Ingredient('bacon', IngredientProperties(50, True, False))]
        assert recipe.cooking_time == (25, 'minutes')
        assert recipe.oven_temperature == (175, 5)
        assert recipe.instructions == [
            {'command': 'take', 'ingredient': 'apple', 'lineno': 12}]
        assert recipe.serves == 10

    def test_invalid_code(self, invalid_code):
        with pytest.raises(ChefSyntaxError) as e:
            chef_parser.parse_recipe(invalid_code)
        assert e.value.msg == 'missing syntax element: method'
