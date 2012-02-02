from chef.errors import ChefError

class ChefRuntimeError(ChefError):
    pass


class InvalidInputError(ChefRuntimeError):
    def __init__(self, value, lineno=None):
        self.value = value
        self.lineno = lineno

    def __repr__(self):
        if self.lineno is None:
            return '%s(%r)' % (self.__class__.__name__, self.value)
        else:
            return '%s(%r, %d)' % (
                self.__class__.__name__, self.value, self.lineno)

    def __str__(self):
        msg = 'invalid input: %r' % self.value
        if self.lineno is not None:
            msg += ' (line %d)' % self.lineno
        return msg


class UndefinedIngredientError(ChefRuntimeError):
    def __init__(self, ingredient, lineno=None):
        self.ingredient = ingredient
        self.lineno = lineno

    def __repr__(self):
        if self.lineno is None:
            return '%s(%r)' % (self.__class__.__name__, self.ingredient)
        else:
            return '%s(%r, %d)' % (
                self.__class__.__name__, self.ingredient, self.lineno)

    def __str__(self):
        msg = 'undefined ingredient: %r' % self.ingredient
        if self.lineno is not None:
            msg += ' (line %d)' % self.lineno
        return msg


class ContainerIDError(ChefRuntimeError):
    def __init__(self, type, id, lineno=None):
        self.type = type
        self.id = 1 if id is None else id
        self.lineno = lineno

    def __repr__(self):
        if self.lineno is None:
            return '%s(%r, %r)' % (self.__class__.__name__, self.type, self.id)
        else:
            return '%s(%r, %r, %d)' % (
                self.__class__.__name__, self.type, self.id, self.lineno)

    def __str__(self):
        raise NotImplementedError(
            'do not raise this exception directly; instead, subclass '
            'this class and define your custom __str__ method')


class InvalidContainerIDError(ContainerIDError):
    def __str__(self):
        msg = 'invalid ordinal identifier for mixing bowl: %r' % (self.type, self.id)
        if self.lineno is not None:
            msg += ' (line %d)' % self.lineno
        return msg


class NonExistingContainerError(ContainerIDError):
    def __str__(self):
        msg = 'the mixing bowl #%d does not exist' % (self.type, self.id)
        if self.lineno is not None:
            msg += ' (line %d)' % self.lineno
        return msg


class EmptyContainerError(ContainerIDError):
    def __str__(self):
        msg = 'the mixing bowl #%d is empty' % (self.type, self.id)
        if self.lineno is not None:
            msg += ' (line %d)' % self.lineno
        return msg


class MissingLoopEndError(ChefRuntimeError):
    def __init__(self, verb, lineno=None):
        self.verb = verb
        self.lineno = lineno

    def __repr__(self):
        if self.lineno is None:
            return '%s(%r)' % (self.__class__.__name__, self.verb)
        else:
            return '%s(%r, %d)' % (self.__class__.__name__, self.verb, self.lineno)

    def __str__(self):
        msg = (
            'the loop with the verb %r does not have a matching '
            'until-statement to mark the end of the loop') % self.verb
        if self.lineno is not None:
            msg += ' (line %d)' % self.lineno
        return msg
