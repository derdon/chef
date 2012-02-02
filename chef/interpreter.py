from __future__ import with_statement

import sys
import random
import argparse
from collections import deque
from operator import add, sub, mul, floordiv as div

from chef import __version__ as chef_version
from chef.parser import parse_recipe
from chef.datastructures import Ingredients, IngredientProperties, undefined
from chef.errors import ChefError
from chef.errors.runtime import InvalidInputError, UndefinedIngredientError,\
        InvalidContainerIDError, NonExistingContainerError,\
        EmptyContainerError, MissingLoopEndError
from chef.utils import verbs_match
from chef.external import pretty


class Interpreter(object):
    def __init__(self, global_ingredients=None, mixing_bowls=None):
        if global_ingredients is None:
            self.global_ingredients = Ingredients([])
        else:
            self.global_ingredients = global_ingredients
        if mixing_bowls is None:
            self.mixing_bowls = [Ingredients([])]
        else:
            self.mixing_bowls = mixing_bowls
        self.baking_dishes = [Ingredients([])]

    @property
    def first_baking_dish(self):
        return self.baking_dishes[0]

    @property
    def first_mixing_bowl(self):
        return self.mixing_bowls[0]

    @property
    def last_mixing_bowl(self):
        return self.mixing_bowls[-1]

    def get_nth_container(self, container_id=None, lineno=None,
            is_mixing_bowl=True):
        container_type = 'mixing bowl' if is_mixing_bowl else 'baking dish'
        if container_id is None:
            if is_mixing_bowl:
                return self.first_mixing_bowl
            else:
                return self.first_baking_dish
        if container_id < 1:
            raise InvalidContainerIDError(container_type, container_id, lineno)
        try:
            if is_mixing_bowl:
                return self.mixing_bowls[container_id - 1]
            else:
                return self.baking_dishes[container_id - 1]
        except IndexError:
            raise NonExistingContainerError(
                container_type, container_id, lineno)

    def get_ingredient_by_name(self, ingredient_name, lineno=None):
        try:
            return self.global_ingredients[ingredient_name]
        except KeyError:
            raise UndefinedIngredientError(ingredient_name, lineno)

    def calculate(self, func, ingredient_name, mixing_bowl_id=None,
            lineno=None):
        ingredient = self.get_ingredient_by_name(ingredient_name, lineno)
        value = ingredient.properties.value
        mixing_bowl = self.get_nth_container(mixing_bowl_id, lineno)
        try:
            top_ingredient = mixing_bowl.top
        except IndexError:
            raise EmptyContainerError('mixing bowl', mixing_bowl_id, lineno)
        value_in_mixing_bowl = top_ingredient.properties.value
        result = func(value_in_mixing_bowl, value)
        # XXX: which ingredient name should be used?
        mixing_bowl[ingredient_name] = IngredientProperties(
            result,
            ingredient.properties.is_dry,
            ingredient.properties.is_liquid)

    def take(self, ingredient_name, lineno=None, stdin=sys.stdin):
        '''This reads a numeric value from STDIN into the ingredient named,
        overwriting any previous value.

        '''
        input = stdin.readline().strip()
        try:
            input_as_int = int(input)
        except ValueError:
            raise InvalidInputError(input, lineno)
        ingredient = self.get_ingredient_by_name(ingredient_name, lineno)
        self.global_ingredients[ingredient_name] = IngredientProperties(
            input_as_int,
            ingredient.properties.is_dry,
            ingredient.properties.is_liquid)

    def put(self, ingredient_name, mixing_bowl_id=None, lineno=None):
        'This puts the ingredient into the nth mixing bowl.'
        try:
            mixing_bowl = self.get_nth_container(mixing_bowl_id, lineno)
        except NonExistingContainerError:
            # create a new mixing bowl if the ID is larger than the current
            # largest mixing bowl ID by 1
            if mixing_bowl_id - 1 == len(self.mixing_bowls):
                mixing_bowl = Ingredients()
                self.mixing_bowls.append(mixing_bowl)
            else:
                raise InvalidContainerIDError(
                    'mixing bowl', mixing_bowl_id, lineno)
        ingredient = self.get_ingredient_by_name(ingredient_name, lineno)
        mixing_bowl.append(ingredient)

    def fold(self, ingredient_name, mixing_bowl_id=None, lineno=None):
        '''This removes the top value from the nth mixing bowl and places it in
        the ingredient.

        '''
        mixing_bowl = self.get_nth_container(mixing_bowl_id, lineno)
        try:
            top_value = mixing_bowl.pop()
        except IndexError:
            raise EmptyContainerError('mixing bowl', mixing_bowl_id, lineno)
        self.global_ingredients[ingredient_name] = top_value

    def add(self, ingredient_name, mixing_bowl_id=None, lineno=None):
        '''This adds the value of ingredient to the value of the ingredient on
        top of the nth mixing bowl and stores the result in the nth mixing
        bowl.

        '''
        self.calculate(add, ingredient_name, mixing_bowl_id, lineno)

    def remove(self, ingredient_name, mixing_bowl_id=None, lineno=None):
        '''This subtracts the value of ingredient from the value of the
        ingredient on top of the nth mixing bowl and stores the result in the
        nth mixing bowl.

        '''
        self.calculate(sub, ingredient_name, mixing_bowl_id, lineno)

    def combine(self, ingredient_name, mixing_bowl_id=None, lineno=None):
        '''This multiplies the value of ingredient by the value of the
        ingredient on top of the nth mixing bowl and stores the result in the
        nth mixing bowl.

        '''
        self.calculate(mul, ingredient_name, mixing_bowl_id, lineno)

    def divide(self, ingredient_name, mixing_bowl_id=None, lineno=None):
        '''This divides the value of ingredient into the value of the
        ingredient on top of the nth mixing bowl and stores the result in the
        nth mixing bowl.

        '''
        self.calculate(div, ingredient_name, mixing_bowl_id, lineno)

    def add_dry(self, lineno=None):
        '''This adds the values of all the dry ingredients together and places
        the result into the nth mixing bowl.

        '''
        raise NotImplementedError()

    def liquefy_ingredient(self, ingredient_name, lineno=None):
        '''This turns the ingredient into a liquid, i.e. a Unicode character
        for output purposes.

        '''
        ingredient = self.get_ingredient_by_name(ingredient_name, lineno)
        self.global_ingredients[ingredient_name] = IngredientProperties(
            ingredient.properties.value, False, True)

    def liquefy_contents(self, mixing_bowl_id=None, lineno=None):
        '''This turns all the ingredients in the nth mixing bowl into a liquid,
        i.e. a Unicode characters for output purposes.

        '''
        mixing_bowl = self.get_nth_container(mixing_bowl_id, lineno)
        for ingredient in list(mixing_bowl):
            mixing_bowl[ingredient.name] = IngredientProperties(
                ingredient.properties.value, False, True)

    def stir_minutes(self, minutes, mixing_bowl_id=None, lineno=None):
        '''This "rolls" the top number ingredients in the nth mixing bowl, such
        that the top ingredient goes down that number of ingredients and all
        ingredients above it rise one place. If there are not that many
        ingredients in the bowl, the top ingredient goes to tbe bottom of the
        bowl and all the others rise one place.

        '''
        mixing_bowl = self.get_nth_container(mixing_bowl_id, lineno)
        mixing_bowl.stir(minutes)

    def stir_ingredient(
            self, ingredient_name, mixing_bowl_id=None, lineno=None):
        '''This rolls the number of ingredients in the nth mixing bowl equal to
        the value of ingredient, such that the top ingredient goes down that
        number of ingredients and all ingredients above it rise one place. If
        there are not that many ingredients in the bowl, the top ingredient
        goes to tbe bottom of the bowl and all the others rise one place.

        '''
        ingredient = self.get_ingredient_by_name(ingredient_name, lineno)
        mixing_bowl = self.get_nth_container(mixing_bowl_id, lineno)
        mixing_bowl.stir(ingredient.properties.value)

    def mix(self, mixing_bowl_id=None, lineno=None):  # pragma: no cover
        'This randomises the order of the ingredients in the nth mixing bowl.'
        mixing_bowl = self.get_nth_container(mixing_bowl_id, lineno)
        random.shuffle(mixing_bowl)

    def clean(self, mixing_bowl_id=None, lineno=None):
        'This removes all the ingredients from the nth mixing bowl.'
        mixing_bowl = self.get_nth_container(mixing_bowl_id, lineno)
        del mixing_bowl[:]

    def pour(self, mixing_bowl_id=None, baking_dish_id=None, lineno=None):
        '''This copies all the ingredients from the nth mixing bowl to the pth
        baking dish, retaining the order and putting them on top of anything
        already in the baking dish.

        '''
        mixing_bowl = self.get_nth_container(mixing_bowl_id, lineno)
        baking_dish = self.get_nth_container(baking_dish_id, lineno, False)
        baking_dish.extend(mixing_bowl)

    def loop_start(self, verb, ingredient_name, following_instructions,
            lineno=None):
        '''The loop executes as follows: The value of ingredient is checked. If
        it is non-zero, the body of the loop executes until it reaches the
        "until" statement. The value of ingredient is rechecked. If it is
        non-zero, the loop executes again. If at any check the value of
        ingredient is zero, the loop exits and execution continues at the
        statement after the "until". Loops may be nested.

        '''
        body = []
        import pprint
        pprint.pprint(following_instructions)
        for instr in following_instructions:
            body.append(instr)
            if instr['command'] == 'loop_end' and verbs_match(verb, instr['verb']):
                break
        else:
            # no matching loop end
            raise MissingLoopEndError(verb, lineno)
        #print 'body: %r' % body
        while True:
            for instruction in body:
                eval_instruction(instruction, following_instructions, self)
            ingredient = self.get_ingredient_by_name(ingredient_name, lineno)
            if ingredient.properties.value == 0:
                break

    def loop_end(self, ingredient_name=None, lineno=None):
        '''If the ingredient appears in this statement, its value is
        decremented by 1 when this statement executes. Otherwise, it only marks
        the end of the loop.

        '''
        if ingredient_name is not None:
            ingredient = self.get_ingredient_by_name(ingredient_name, lineno)
            new_value = ingredient.properties.value - 1
            self.global_ingredients[ingredient_name] = IngredientProperties(
                new_value,
                ingredient.properties.is_dry,
                ingredient.properties.is_liquid)

    def serves(self, num_of_diners, stdout=sys.stdout, encoding='utf-8'):
        '''This statement writes to STDOUT the contents of the first
        number-of-diners baking dishes. It begins with the 1st baking dish,
        removing values from the top one by one and printing them until the
        dish is empty, then progresses to the next dish, until all the dishes
        have been printed.

        '''
        for baking_dish in self.baking_dishes[:num_of_diners]:
            while baking_dish:
                ingredient = baking_dish.pop()
                if ingredient.properties.is_liquid:
                    convert = unichr
                else:
                    convert = unicode
                value = convert(ingredient.properties.value).encode(encoding)
                stdout.write(value)
        stdout.flush()


def eval_instruction(instruction, instructions, interpreter):
    cmd = instruction['command']
    f = getattr(interpreter, cmd)
    ingredient = instruction.get('ingredient')
    mixing_bowl_id = instruction.get('mixing_bowl_id')
    if cmd in ('take', 'liquefy_ingredient', 'loop_end'):
        args = [ingredient]
    elif cmd in ('put', 'fold', 'add', 'remove', 'combine', 'divide',
            'stir_ingredient'):
        args = [ingredient, mixing_bowl_id]
    elif cmd == 'add_dry':
        args = []
    elif cmd in ('liquefy_contents', 'mix', 'clean'):
        args = [mixing_bowl_id]
    elif cmd == 'stir_minutes':
        args = [mixing_bowl_id, instruction['minutes']]
    elif cmd == 'pour':
        args = [mixing_bowl_id, instruction['baking_dish_id']]
    elif cmd == 'loop_start':
        args = [instruction['verb'], ingredient, instructions]
    else:
        assert False
    args.append(instruction['lineno'])
    #print 'function: %r, args: %r' % (f.__name__, args)
    f(*args)


def interpret_recipe(recipe):
    interpreter = Interpreter(recipe.ingredients)
    instructions = deque(recipe.instructions)
    while instructions:
        instruction = instructions.popleft()
        eval_instruction(instruction, instructions, interpreter)
    if recipe.serves is not undefined:
        interpreter.serves(recipe.serves)


def interpret_file(f):
    interpret_recipe(parse_recipe(f))


def parse_args(argv):
    parser = argparse.ArgumentParser(prog='chef')
    parser.add_argument(
        '--version', action='version', version='%(prog)s ' + chef_version)
    parser.add_argument(
        '-f', '--file',
        help='path to the file which has to be parsed or evaluated')
    parser.add_argument(
        '-p', '--parse-only', action='store_true', default=False,
        help='only parse, do not interpret')
    # NOTE: debug mode is not implemented yet
    #parser.add_argument(
    #    '-d', '--debug', action='store_true', default=False,
    #    help='enable the deubg mode')
    return parser.parse_args(argv)


def main(argv=None):
    def user_friendly_excepthook(exctype, value, traceback):
        'uses only a custom output if exception is ChefError'
        if ChefError in exctype.mro():
            # FIXME: show bold and red output!
            # -> relevant line bold, error message red
            print value
            print
            with open(filename) as f:
                for lineno, line in enumerate(f):
                    # print two lines before and after the affected invalid
                    # line as context (inlcuding line numbers)
                    # TODO: right-align the col num, don't use \t
                    if lineno in xrange(value.lineno - 2, value.lineno + 3):
                        print '%d\t%s' % (lineno, line),
        else:
            original_excepthook(exctype, value, traceback)
    original_excepthook = sys.excepthook
    sys.excepthook = user_friendly_excepthook
    if argv is None:
        argv = sys.argv[1:]
    args = parse_args(argv)
    filename = args.file
    if filename:
        with open(filename) as f:
            parsed_recipe = parse_recipe(f)
    else:
        parsed_recipe = parse_recipe(sys.stdin)
    if args.parse_only:
        pretty.pprint(parsed_recipe)
    else:
        interpret_recipe(parsed_recipe)
