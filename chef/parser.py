import re
from functools import partial

from chef.datastructures import Recipe, IngredientProperties,\
        Ingredients, unknown, undefined
from chef.validators import validate_title, validate_ordinal_id_suffix,\
        validate_measure_type, validate_cooking_time, validate_time_declaration
from chef.errors import syntax as syntax_errors
import chef.utils as chef_utils

DRY_MEASURE_PATTERN = r'k?g|pinch(?:es)?'
LIQUID_MEASURE_PATTERN = r'm?l|dash(?:es)?'
DRY_OR_LIQUID_MEASURE_PATTERN = r'cups?|teaspoons?|tablespoons?'
MEASURE_PATTERN = r'|'.join((
    DRY_MEASURE_PATTERN,
    LIQUID_MEASURE_PATTERN,
    DRY_OR_LIQUID_MEASURE_PATTERN))

MEASURE_TYPE_PATTERN = 'heaped|level'

# [initial-value] [[measure-type] measure] ingredient-name
INGREDIENT_LIST_ITEM_PATTERN = (
    r'((?P<initial_value>\d+?) )?'
    r'(((?P<measure_type>%s) )?(?P<measure>%s) )?'
    r'(?P<name>.+)' % (
        MEASURE_TYPE_PATTERN, MEASURE_PATTERN))

# Cooking time: time (hour[s] | minute[s]).
COOKING_TIME_PATTERN = (
    r'Cooking time: (?P<cooking_time>\d+?) (?P<unit>hours?|minutes?)\.')

# Pre-heat oven to temperature degrees Celsius [(gas mark mark)].
OVEN_TEMPERATURE_PATTERN = (
    r'Pre-heat oven to (?P<temperature>\d+) degrees Celsius'
    r'(?: \(gas mark (?P<gas_mark>\d+)\))?\.')

ORDINAL_IDENTIFIER_PATTERN = r'([1-9]\d*?)(st|nd|rd|th)'

SERVES_PATTERN = r'Serves ([1-9]\d*)\.'


def parse_ordinal_identifier(ordinal_identifier, lineno=None):
    '''Checks if the string `ordinal_identifier` is a number followed by one of
    the suffixes st, nd, rd or th. Raises
    chef.validators.OrdinalIdentifierError if it does not. Else, return the
    appertaining number as an integer.

    '''
    m = re.match(ORDINAL_IDENTIFIER_PATTERN, ordinal_identifier)
    if m is None:
        raise syntax_errors.OrdinalIdentifierError(ordinal_identifier, lineno)
    num_str, suffix = m.groups()
    validate_ordinal_id_suffix(num_str, suffix, lineno)
    return int(num_str)


def detect_ingredient_state(measure, measure_type=None, lineno=None):
    '''If there is no measure given, the ingredient is neither dry nor liquid.
    If there is any valid measure_type given, the ingredient is dry and needs
    no further analysis. If the given measure is "g", "kg", "pinch" or
    "pinches", it is dry. If it is "l", "ml", "dash" or "dashes", it is
    "liquid". If it is "cup(s)", "teaspoon(s)" or "tablespoon(s)", it is not
    known if the ingredient is dry or liquid. This function returns a tuple in
    the form (is_dry, is_liquid).

    '''
    if measure is None:
        is_dry, is_liquid = False, False
    elif measure_type is not None:
        validate_measure_type(measure, measure_type, lineno)
        is_dry, is_liquid = True, False
    elif re.match(DRY_MEASURE_PATTERN, measure) is not None:
        is_dry, is_liquid = True, False
    elif re.match(LIQUID_MEASURE_PATTERN, measure) is not None:
        is_dry, is_liquid = False, True
    elif re.match(DRY_OR_LIQUID_MEASURE_PATTERN, measure) is not None:
        is_dry, is_liquid = unknown, unknown
    else:
        raise ValueError('invalid measure: %r' % measure)
    return is_dry, is_liquid


def parse_ingredient_list(ingredient_list, lineno):
    ingredients = Ingredients()
    for item in ingredient_list.splitlines():
        m = re.match(INGREDIENT_LIST_ITEM_PATTERN, item)
        if m is None:
            raise syntax_errors.InvalidCommandError('ingredient', lineno)
        try:
            value = int(m.group('initial_value'))
        except TypeError:
            value = None
        is_dry, is_liquid = detect_ingredient_state(m.group('measure'))
        name = m.group('name')
        properties = IngredientProperties(value, is_dry, is_liquid)
        ingredients[name] = properties
        lineno += 1
    return ingredients, lineno


def is_cooking_time(line):
    m = re.match(COOKING_TIME_PATTERN, line)
    return m is not None


def parse_cooking_time(line, lineno=None):
    m = re.match(COOKING_TIME_PATTERN, line)
    if not is_cooking_time(line):
        raise syntax_errors.InvalidCookingTimeError(lineno)
    time, unit = m.groups()
    validate_cooking_time(time, unit, lineno)
    cooking_time = int(time)
    return cooking_time, unit


def is_oven_temperature(line):
    m = re.match(OVEN_TEMPERATURE_PATTERN, line)
    return m is not None


def parse_oven_temperature(line, lineno=None):
    m = re.match(OVEN_TEMPERATURE_PATTERN, line)
    if m is None:
        raise syntax_errors.InvalidOvenTemperature(lineno)
    elements = m.groups()
    parsed_elements = []
    for elem in elements:
        try:
            parsed_elem = int(elem)
        except TypeError:
            parsed_elem = None
        finally:
            parsed_elements.append(parsed_elem)
    return tuple(parsed_elements)


def get_ordinal_id(match_object, group_num, lineno=None):
    ordinal_identifier = match_object.group(group_num)
    if ordinal_identifier is None:
        return None
    else:
        return parse_ordinal_identifier(ordinal_identifier, lineno)


def parse_ingredient_preposition_nth_mixing_bowl(cmd, preposition, statement,
                                                 lineno=None):
    # cmd ingredient preposition [nth ]mixing bowl.
    #pattern = '(.+?) %s (?:(%s )|the )mixing bowl\.' % (
    pattern = '(.+?) %s (?:(%s) )?mixing bowl\.' % (
        preposition, ORDINAL_IDENTIFIER_PATTERN)
    m = re.match(pattern, statement)
    if m is None:
        raise syntax_errors.InvalidCommandError(cmd, lineno)
    ingredient = m.group(1)
    mixing_bowl_id = get_ordinal_id(m, 2)
    return {
        'command': cmd.lower(),
        'ingredient': ingredient,
        'mixing_bowl_id': mixing_bowl_id}


def parse_ingredient_optional_preposition_nth_mixing_bowl(cmd, preposition,
                                                          statement,
                                                          lineno=None):
    # cmd ingredient[ to [nth ]mixing bowl].
    pattern_with_suffix = r'(.+?)(?: %s (%s )?mixing bowl)\.' % (
        preposition, ORDINAL_IDENTIFIER_PATTERN)
    m = re.match(pattern_with_suffix, statement)
    if m is None:
        pattern_without_suffix = r'(.+?)\.'
        m = re.match(pattern_without_suffix, statement)
        if m is None:
            raise syntax_errors.InvalidCommandError(cmd, lineno)
        mixing_bowl_id = None
    else:
        mixing_bowl_id = get_ordinal_id(m, 2)
    ingredient = m.group(1)
    return {
        'command': cmd.lower(),
        'ingredient': ingredient,
        'mixing_bowl_id': mixing_bowl_id}


def parse_take(statement, lineno=None):
    # Take ingredient from refrigerator.
    m = re.match('(.+?) from refrigerator\.', statement)
    if m is None:
        raise syntax_errors.InvalidCommandError('Take', lineno)
    return {'command': 'take', 'ingredient': m.group(1)}


def parse_put(statement, lineno=None):
    # Put ingredient into [nth] mixing bowl.
    return parse_ingredient_preposition_nth_mixing_bowl(
        'Put', 'into', statement, lineno)


def parse_fold(statement, lineno=None):
    # Fold ingredient into [nth] mixing bowl.
    return parse_ingredient_preposition_nth_mixing_bowl(
        'Fold', 'into', statement, lineno)


def parse_add(statement, lineno=None):
    # Add ingredient [to [nth] mixing bowl].
    # attempt to parse 'Add dry ingredients' command before trying to parse
    # 'Add'
    try:
        return parse_add_dry(statement, lineno)
    except syntax_errors.InvalidCommandError:
        if statement.startswith('dry ingredients'):
            raise
        else:
            return parse_ingredient_optional_preposition_nth_mixing_bowl(
                'Add', 'to', statement, lineno)


def parse_remove(statement, lineno=None):
    # Remove ingredient [from [nth] mixing bowl].
    return parse_ingredient_optional_preposition_nth_mixing_bowl(
        'Remove', 'from', statement, lineno)


def parse_combine(statement, lineno=None):
    # Combine ingredient [into [nth] mixing bowl].
    return parse_ingredient_optional_preposition_nth_mixing_bowl(
        'Combine', 'into', statement, lineno)


def parse_divide(statement, lineno=None):
    # Divide ingredient [into [nth] mixing bowl].
    return parse_ingredient_optional_preposition_nth_mixing_bowl(
        'Divide', 'into', statement, lineno)


def parse_add_dry(statement, lineno=None):
    # Add dry ingredients [to [nth] mixing bowl].
    pattern = (
        'dry ingredients'
        '(?: to (%s )mixing bowl)?\.' % ORDINAL_IDENTIFIER_PATTERN)
    m = re.match(pattern, statement)
    if m is None:
        raise syntax_errors.InvalidCommandError('Add dry', lineno)
    mixing_bowl_id = get_ordinal_id(m, 1)
    return {'command': 'add_dry', 'mixing_bowl_id': mixing_bowl_id}


def parse_liquefy_ingredient(statement, lineno=None):
    # Liquefy ingredient.
    m = re.match('(.+?)\.', statement)
    if m is None:
        raise syntax_errors.InvalidCommandError('Liquefy', lineno)
    return {'command': 'liquefy_ingredient', 'ingredient': m.group(1)}


def parse_liquefy_contents(statement, lineno=None):
    # Liquefy contents of the [nth] mixing bowl.
    pattern = (
        'contents of the( (%s))? mixing bowl\.' % ORDINAL_IDENTIFIER_PATTERN)
    m = re.match(pattern, statement)
    if m is None:
        return parse_liquefy_ingredient(statement, lineno)
    mixing_bowl_id = get_ordinal_id(m, 2)
    return {
        'command': 'liquefy_contents',
        'mixing_bowl_id': mixing_bowl_id}


def parse_stir_minutes(statement, lineno=None):
    # Stir [the [nth] mixing bowl] for number minutes.
    pattern = '(?:the( (%s))? mixing bowl )?for (\d+?) minutes\.' % (
        ORDINAL_IDENTIFIER_PATTERN)
    m = re.match(pattern, statement)
    if m is None:
        raise syntax_errors.InvalidCommandError('Stir', lineno)
    return {
        'command': 'stir_minutes',
        'mixing_bowl_id': get_ordinal_id(m, 2),
        'minutes': int(m.group(5))}


def parse_stir_ingredient(statement, lineno=None):
    # Stir ingredient into the [nth] mixing bowl.
    pattern = '(.+?) into the(?: (%s))? mixing bowl\.' % (
        ORDINAL_IDENTIFIER_PATTERN)
    m = re.match(pattern, statement)
    if m is None:
        raise syntax_errors.InvalidCommandError('Stir', lineno)
    return {
        'command': 'stir_ingredient',
        'ingredient': m.group(1),
        'mixing_bowl_id': get_ordinal_id(m, 2)}


def parse_stir(statement, lineno=None):
    # If the first word of `statement` is either 'the' or 'for', then the
    # command is in the first form. Otherwise, it is the last form, i.e. the
    # first word is an ingredient.
    first_word, _ = statement.split(' ', 1)
    if first_word in ('the', 'for'):
        return parse_stir_minutes(statement, lineno)
    else:
        return parse_stir_ingredient(statement, lineno)


def parse_mix(statement, lineno=None):
    # Mix [the [nth] mixing bowl] well.
    pattern = '(the ((%s) )?mixing bowl )?well\.' % ORDINAL_IDENTIFIER_PATTERN
    m = re.match(pattern, statement)
    if m is None:
        raise syntax_errors.InvalidCommandError('Mix', lineno)
    mixing_bowl_id = get_ordinal_id(m, 2)
    return {
        'command': 'mix', 'mixing_bowl_id': mixing_bowl_id}


def parse_clean(statement, lineno=None):
    # Clean [nth] mixing bowl.
    pattern = '((%s) )?mixing bowl\.' % ORDINAL_IDENTIFIER_PATTERN
    m = re.match(pattern, statement)
    if m is None:
        raise syntax_errors.InvalidCommandError('Clean', lineno)
    mixing_bowl_id = get_ordinal_id(m, 2)
    return {'command': 'clean', 'mixing_bowl_id': mixing_bowl_id}


def parse_pour(statement, lineno=None):
    # Pour contents of the [nth] mixing bowl into the [pth] baking dish.
    pattern = (
        'contents of the( (%(ord)s))? mixing bowl into the'
        '( (%(ord)s))? baking dish\.' % {'ord': ORDINAL_IDENTIFIER_PATTERN})
    m = re.match(pattern, statement)
    if m is None:
        raise syntax_errors.InvalidCommandError('Pour', lineno)
    get_id = partial(get_ordinal_id, m)
    mixing_bowl_id = get_id(2)
    baking_dish_id = get_id(6)
    return {
        'command': 'pour',
        'mixing_bowl_id': mixing_bowl_id,
        'baking_dish_id': baking_dish_id}


def parse_refrigerate(statement, lineno=None):
    # Refrigerate [for number hours].
    pattern = '(for ([1-9]\d*?) (hours?))?\.'
    m = re.match(pattern, statement)
    if m is None:
        raise syntax_errors.InvalidCommandError('Refrigerate', lineno)
    hours = m.group(2)
    hour_or_hours = m.group(3)
    # "1 hours" and "2 hour" are invalid
    validate_time_declaration(hours, hour_or_hours, lineno)
    return {
        'command': 'refrigerate',
        'hours': int(hours) if hours is not None else None}


def parse_loop_start(verb, statement, lineno=None):
    # Verb the ingredient.
    m = re.match('the (.+?)\.', statement)
    if m is None:
        raise syntax_errors.InvalidCommandError(verb, lineno)
    return {
        'command': 'loop_start', 'verb': verb, 'ingredient': m.group(1)}


def parse_loop_end(verb, statement, lineno=None):
    # Verb [the ingredient] until verbed.
    m = re.match('(the (.+?) )?until ([a-z]+ed)\.', statement)
    if m is None:
        raise syntax_errors.InvalidCommandError(verb, lineno)
    return {
        'command': 'loop_end', 'verb': m.group(3), 'ingredient': m.group(2)}


def parse_loop(verb, statement, lineno=None):
    try:
        return parse_loop_end(verb, statement, lineno)
    except syntax_errors.InvalidCommandError:
        return parse_loop_start(verb, statement, lineno)


def parse_instruction(line, lineno=None):
    method, statement = line.split(' ', 1)
    functions = {
        'Take': parse_take,
        'Put': parse_put,
        'Fold': parse_fold,
        'Add': parse_add,
        'Remove': parse_remove,
        'Combine': parse_combine,
        'Divide': parse_divide,
        'Liquefy': parse_liquefy_contents,
        'Stir': parse_stir,
        'Mix': parse_mix,
        'Clean': parse_clean,
        'Pour': parse_pour,
        'Refrigerate': parse_refrigerate}
    func = functions.get(method)
    if func is None:
        try:
            d = parse_loop(method, statement, lineno)
        except syntax_errors.InvalidCommandError:
            raise syntax_errors.ChefSyntaxError(
                'invalid method name: %r' % method, lineno)
    else:
        d = func(statement, lineno)
    d['lineno'] = lineno
    return d


def parse_method(paragraph, lineno):
    # remove the introductory line if it exists
    if paragraph.startswith('Method.\n'):
        paragraph = paragraph.lstrip('Method.\n')
    parsed_instructions = []
    for instr in paragraph.rstrip('.').split('.'):
        #lineno += instr.count('\n')
        lineno += 1
        if instr.strip():
            parsed_instructions.append(
                parse_instruction(instr.strip() + '.', lineno))
    return parsed_instructions, lineno


def is_serves(line):
    m = re.match(SERVES_PATTERN, line)
    return m is not None


def parse_serves(line, lineno):
    m = re.match(SERVES_PATTERN, line)
    num_of_diners = int(m.group(1))
    return num_of_diners


def update_current_par_and_line(f):
    cur_par = chef_utils.read_until_blank_line(f)
    cur_line = cur_par.split('\n', 1)[0]
    return cur_par, cur_line


def parse_serves_if_possible(f, lineno):
    cur_par, cur_line = update_current_par_and_line(f)
    lineno += cur_par.count('\n')
    if is_serves(cur_line):
        serves = parse_serves(cur_line, lineno)
    else:
        serves = undefined
    return serves, lineno


def parse_recipe(f):
    consumed_comments = False
    title = f.readline().rstrip()
    validate_title(title)
    if f.readline() != '\n':
        raise syntax_errors.MissingEmptyLineError(2)
    lineno = 2
    parsed_ingredients = parsed_cooking_time = parsed_oven_temperature = False
    # set some default values for recipe elements
    ingredients = Ingredients()
    cooking_time = oven_temperature = serves = undefined
    while True:
        cur_par, cur_line = update_current_par_and_line(f)
        lineno += 1
        if cur_line == 'Ingredients.':
            headline, ingredient_list = cur_par.split('\n', 1)
            ingredients, lineno = parse_ingredient_list(
                ingredient_list, lineno)
            parsed_ingredients = True
        elif is_cooking_time(cur_line):
            cooking_time = parse_cooking_time(cur_line, lineno)
            parsed_cooking_time = True
        elif is_oven_temperature(cur_line):
            oven_temperature = parse_oven_temperature(cur_line, lineno)
            parsed_oven_temperature = True
        elif cur_line == 'Method.':
            if parsed_ingredients:
                lineno += 1
            if parsed_cooking_time:
                lineno += 1
            if parsed_oven_temperature:
                lineno += 1
            parsed_instructions, lineno = parse_method(cur_par, lineno)
            serves, lineno = parse_serves_if_possible(f, lineno)
            break
        else:
            if consumed_comments:
                raise syntax_errors.ChefSyntaxError(
                    'missing syntax element: method', lineno)
            else:
                lineno += cur_par.count('\n')
                consumed_comments = True
    # make sure the whole file content is exhausted
    rest = f.read()
    assert rest == ''
    return Recipe(
        ingredients, cooking_time,
        oven_temperature, parsed_instructions, serves)
