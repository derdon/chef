from chef.errors import ChefError


class ChefSyntaxError(ChefError):
    pass


class CustomSyntaxError(ChefSyntaxError):
    def __init__(self, lineno=None):
        self.lineno = lineno


class MissingTitleError(CustomSyntaxError):
    msg = 'missing title'


class MissingTrailingFullStopError(CustomSyntaxError):
    msg = 'missing trailing full stop'


class MissingEmptyLineError(CustomSyntaxError):
    msg = 'missing empty line'


class InvalidCookingTimeError(CustomSyntaxError):
    msg = 'invalid cooking time'


class InvalidOvenTemperature(CustomSyntaxError):
    msg = 'invalid oven temperature'


class InvalidMeasureTypeValue(CustomSyntaxError):
    def __init__(self, measure_type, lineno=None):
        self.measure_type = measure_type
        self.lineno = lineno

    def __repr__(self):
        if self.lineno is None:
            return '%s(%r)' % (self.__class__.__name__, self.measure_type)
        else:
            return '%s(%r, %d)' % (
                self.__class__.__name__, self.measure_type, self.lineno)

    def __str__(self):
        msg = (
            'invalid measure type value (%r); only the values "heaped" and'
            '"level" are allowed' % self.measure_type)
        if self.lineno is not None:
            msg += ' (line %d)' % self.lineno
        return msg


class NonMatchingMeasureTypeError(CustomSyntaxError):
    def __init__(self, measure, measure_type, lineno=None):
        self.measure = measure
        self.measure_type = measure_type
        self.lineno = lineno

    def __repr__(self):
        if self.lineno is None:
            return '%s(%r, %r)' % (
                self.__class__.__name__, self.measure, self.measure_type)
        else:
            return '%s(%r, %r, %d)' % (
                self.__class__.__name__, self.measure, self.measure_type,
                self.lineno)

    def __str__(self):
        msg = (
            'the measure %r and the measure type %r '
            'do not form a valid measure declaration')
        if self.lineno is None:
            self.msg += ' (line %d)' % self.lineno
        return msg


class NotAllowedTimeError(ChefSyntaxError):
    def __init__(self, time, lineno=None):
        self.time = time
        self.lineno = lineno

    def __repr__(self):
        if self.lineno is None:
            return '%s(%r)' % (self.__class__.__name__, self.time)
        else:
            return '%s(%d, %d)' % (
                self.__class__.__name__, self.time, self.lineno)

    def __str__(self):
        msg = (
            'the time %d is too low; '
            'only positive values are allowed' % self.time)
        if self.lineno is not None:
            msg += ' (line %d)' % self.lineno
        return msg


class OrdinalIdentifierError(ChefSyntaxError):
    def __init__(self, ordinal_identifier, lineno=None):
        self.ordinal_identifier = ordinal_identifier
        self.lineno = lineno

    def __repr__(self):
        if self.lineno is None:
            return '%s(%r)' % (
                self.__class__.__name__, self.ordinal_identifier)
        else:
            return '%s(%r, %d)' % (
                self.__class__.__name__, self.ordinal_identifier, self.lineno)

    def __str__(self):
        msg = 'not a valid ordinal identifier: %r' % self.ordinal_identifier
        if self.lineno is not None:
            msg += ' (line %d)' % self.lineno
        return msg


class NonMatchingSuffixError(OrdinalIdentifierError):
    def __init__(self, number, suffix, lineno=None):
        self.number = number
        self.suffix = suffix
        self.lineno = lineno

    def __repr__(self):
        if self.lineno is None:
            return '%s(%d, %s)' % (
                self.__class__.__name__,
                self.number,
                self.suffix)
        else:
            return '%s(%d, %s, %d)' % (
                self.__class__.__name__,
                self.number,
                self.suffix,
                self.lineno)

    def __str__(self):
        msg = (
            'the number %d and the suffix %r do not form a valid '
            'ordinal identifier' % (self.number, self.suffix))
        if self.lineno is not None:
            msg += ' (line %d)' % self.lineno
        return msg


class NonMatchingUnitError(ChefSyntaxError):
    def __init__(self, number, unit, lineno=None):
        self.number = number
        self.unit = unit
        self.lineno = lineno

    def __repr__(self):
        if self.lineno is None:
            return '%s(%d, %s)' % (
                self.__class__.__name__, self.number, self.unit)
        else:
            return '%s(%d, %s, %d)' % (
                self.__class__.__name__,
                self.number,
                self.unit,
                self.lineno)

    def __str__(self):
        msg = (
            'the number %d and the unit %r do not form a valid '
            'cooking time' % (self.number, self.unit))
        if self.lineno is not None:
            msg += ' (line %d)' % self.lineno
        return msg


class InvalidTimeDeclarationError(ChefSyntaxError):
    def __init__(self, hours, format, lineno=None):
        self.hours = hours
        self.format = format

    def __repr__(self):
        if self.lineno is None:
            return '%s(%r, %r)' % (
                self.__class__.__name__, self.hours, self.format)
        else:
            return '%s(%r, %r, %d)' % (
                self.__class__.__name__, self.hours, self.format, self.lineno)

    def __str__(self):
        msg = "invalid time declaration: '%d %s'" % (self.hours, self.format)
        if self.lineno is not None:
            msg += ' (line %d)' % self.lineno
        return msg


class InvalidCommandError(ChefSyntaxError):
    def __init__(self, command, lineno=None):
        self.cmd = command
        self.lineno = lineno

    def __repr__(self):
        if self.lineno is None:
            return '%s(%r)' % (self.__class__.__name__, self.cmd)
        else:
            return '%s(%r, %d)' % (
                self.__class__.__name__, self.cmd, self.lineno)

    def __str__(self):
        msg = 'invalid command %r' % self.cmd
        if self.lineno is not None:
            msg += ' (line %d)' % self.lineno
        return msg
