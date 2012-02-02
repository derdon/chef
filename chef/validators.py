from operator import or_

from chef.errors import syntax as syntax_errors


def validate_title(title):
    'Validate the title of a recipe by checking for a trailing full stop'
    if not title:
        raise syntax_errors.MissingTitleError()
    if title[-1] != '.':
        raise syntax_errors.MissingTrailingFullStopError(1)


def validate_ordinal_id_suffix(number, suffix, lineno=None):
    '''Check if the given number and suffix can be combined to a *senseful*
    ordinal number. Examples: `1th` is not a senseful ordinal identifier, so
    ``validate_ordinal_id_suffix('1', 'th') will return ``False``, whereas
    `2nd` is a senseful ordinal identifier, so
    validate_ordinal_id_suffix('2', 'nd') will return ``True``. Keep in mind
    that if you use these parameters to call the function
    ``validate_ordinal_identifier``, it will return ``True`` for both versions.

    '''
    num = int(number)
    if suffix == 'st':
        if not (num != 11 and number.endswith('1')):
            raise syntax_errors.NonMatchingSuffixError(num, suffix)
    elif suffix == 'nd':
        if not (num != 12 and number.endswith('2')):
            raise syntax_errors.NonMatchingSuffixError(num, suffix)
    elif suffix == 'rd':
        if not (num != 13 and number.endswith('3')):
            raise syntax_errors.NonMatchingSuffixError(num, suffix)
    else:
        last_digit = number[-1]
        assert suffix == 'th'
        if not or_(
                num in (11, 12, 13), last_digit not in set(['1', '2', '3'])):
            raise syntax_errors.NonMatchingSuffixError(num, suffix)


def validate_value_measure(value, measure):
    # FIXME
    # validate_value_measure('3', 'teaspoon') -> raise NonMatchingMeasureError
    # (because it must be 'teaspoons', with an s.)
    raise NotImplementedError()


def validate_measure_type(measure, measure_type, lineno=None):
    if measure_type not in ('heaped', 'level'):
        raise syntax_errors.InvalidMeasureTypeValue(measure_type, lineno)
    valid_measure_values = [
        'pinch', 'pinches', 'cup', 'cups',
        'teaspoon', 'teaspoons', 'tablespoon', 'tablespoons']
    if measure not in valid_measure_values:
        raise syntax_errors.NonMatchingMeasureTypeError(
            measure, measure_type, lineno)


def validate_cooking_time(time, unit, lineno=None):
    try:
        cooking_time = int(time)
    except ValueError:
        raise syntax_errors.InvalidCookingTimeError(lineno)
    if cooking_time < 1:
        raise syntax_errors.NotAllowedTimeError(cooking_time, lineno)
    if cooking_time == 1 and unit.endswith('s') or \
            cooking_time > 1 and not unit.endswith('s'):
        raise syntax_errors.NonMatchingUnitError(cooking_time, unit, lineno)


def validate_time_declaration(hours, format, lineno=None):
    if hours is None:
        return
    hours = int(hours)
    if hours == 1 and format == 'hours' or hours > 1 and format == 'hour':
        raise syntax_errors.InvalidTimeDeclarationError(hours, format, lineno)
