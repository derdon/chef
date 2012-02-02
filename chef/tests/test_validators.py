from __future__ import with_statement

from itertools import imap

import pytest

from chef.errors import syntax as syntax_errors
from chef.validators import validate_title, validate_ordinal_id_suffix,\
        validate_measure_type, validate_cooking_time


class TestValidateTitle(object):
    def test_missing(self):
        with pytest.raises(syntax_errors.MissingTitleError):
            validate_title('')

    def test_dotless(self):
        with pytest.raises(syntax_errors.MissingTrailingFullStopError) as e:
            validate_title('A title without a dot\n')
        assert e.value.lineno == 1


class TestValidateOrdinalIDSuffix(object):
    params = {
        'test_st': [
            {'number': '2'},
            {'number': '3'},
            {'number': '4'},
            {'number': '11'}],
        'test_nd': [
            {'number': '1'},
            {'number': '3'},
            {'number': '4'},
            {'number': '12'}],
        'test_rd': [
            {'number': '1'},
            {'number': '2'},
            {'number': '4'},
            {'number': '13'}],
        'test_th': [
            {'number': '1'},
            {'number': '2'},
            {'number': '3'},
            {'number': '21'},
            {'number': '22'},
            {'number': '23'}]
    }

    @classmethod
    def setup_class(cls):
        cls.st_numbers = [11, 4, 3, 2]
        cls.nd_numbers = [12, 4, 3, 1]
        cls.rd_numbers = [13, 4, 2, 1]
        cls.th_numbers = [23, 22, 21, 3, 2, 1]

    @classmethod
    def teardown_class(cls):
        number_lists = [
            cls.st_numbers,
            cls.nd_numbers,
            cls.rd_numbers,
            cls.th_numbers]
        is_empty_list = lambda l: l == []
        assert all(imap(is_empty_list, number_lists))

    def test_st(self, number):
        with pytest.raises(syntax_errors.NonMatchingSuffixError) as e:
            validate_ordinal_id_suffix(number, 'st')
        # muahaha, side effects!
        assert e.value.number == self.st_numbers.pop()
        assert e.value.suffix == 'st'

    def test_nd(self, number):
        with pytest.raises(syntax_errors.NonMatchingSuffixError) as e:
            validate_ordinal_id_suffix(number, 'nd')
        # muahaha, side effects!
        assert e.value.number == self.nd_numbers.pop()
        assert e.value.suffix == 'nd'

    def test_rd(self, number):
        with pytest.raises(syntax_errors.NonMatchingSuffixError) as e:
            validate_ordinal_id_suffix(number, 'rd')
        # muahaha, side effects!
        assert e.value.number == self.rd_numbers.pop()
        assert e.value.suffix == 'rd'

    def test_th(self, number):
        with pytest.raises(syntax_errors.NonMatchingSuffixError) as e:
            validate_ordinal_id_suffix(number, 'th')
        # muahaha, side effects!
        assert e.value.number == self.th_numbers.pop()
        assert e.value.suffix == 'th'


class TestValidateMeasureType(object):
    params = {
        'test_non_matching_measure_type': [
            {'measure': 'g'},
            {'measure': 'kg'},
            {'measure': 'ml'},
            {'measure': 'l'},
            {'measure': 'dash'},
            {'measure': 'dashes'}]}

    def test_invalid_measure_type_value(self):
        empty_measure = ''
        with pytest.raises(syntax_errors.InvalidMeasureTypeValue):
            validate_measure_type(empty_measure, 'foo')

    def test_non_matching_measure_type(self, measure):
        with pytest.raises(syntax_errors.NonMatchingMeasureTypeError):
            validate_measure_type(measure, 'heaped')
        with pytest.raises(syntax_errors.NonMatchingMeasureTypeError):
            validate_measure_type(measure, 'level')


class TestValidateCookingTime(object):
    params = {
        'test_nonmatching_unit': [
            {'time': '3', 'unit': 'minute'},
            {'time': '5', 'unit': 'hour'},
            {'time': '1', 'unit': 'minutes'},
            {'time': '1', 'unit': 'hours'}]}

    def test_invalid_time_without_lineno(self):
        with pytest.raises(syntax_errors.InvalidCookingTimeError) as e:
            validate_cooking_time('eek', 'minutes')
        assert e.value.lineno is None

    def test_invalid_time_with_lineno(self):
        with pytest.raises(syntax_errors.InvalidCookingTimeError) as e:
            validate_cooking_time('meh', 'hours', 42)
        assert e.value.lineno == 42

    def test_zero_cooking_time(self):
        with pytest.raises(syntax_errors.NotAllowedTimeError) as e:
            validate_cooking_time('0', 'minutes')
        assert e.value.time == 0

    def test_nonmatching_unit(self, time, unit):
        with pytest.raises(syntax_errors.NonMatchingUnitError) as e:
            validate_cooking_time(time, unit)
        assert e.value.number == int(time)
        assert e.value.unit == unit
