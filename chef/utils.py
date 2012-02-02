import re
from string import ascii_lowercase

VOWELS = frozenset('aeiou')
CONSONANTS = frozenset(ascii_lowercase) - VOWELS
_double_consonant_pattern = '[a-z]+?[%s]{2}' % ''.join(CONSONANTS)
_double_consonant_present_pattern = re.compile(_double_consonant_pattern)
_double_consonant_past_pattern = re.compile(_double_consonant_pattern + 'ed')


def read_until_blank_line(f):
    return ''.join(iter(f.next, '\n'))


def verbs_match(present_form, past_form):
    fst, snd = map(str.lower, [present_form, past_form])
    if fst.endswith('e'):
        return snd.endswith('d') and fst == snd[:-1]
    elif re.match(_double_consonant_past_pattern, snd):
        if re.match(_double_consonant_present_pattern, fst):
            return fst == snd[:-2]
        else:
            return fst == snd[:-3]
    else:
        return snd.endswith('ed') and fst == snd[:-2]
