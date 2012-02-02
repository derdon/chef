from chef.utils import read_until_blank_line, verbs_match


class TestReadUntilBlankLine(object):
    def test_one_blank_line(self, fp_with_one_blank_line):
        paragraph = read_until_blank_line(fp_with_one_blank_line)
        assert paragraph == '1st\n2nd\n3rd\n'
        rest = fp_with_one_blank_line.read()
        assert rest == '4th\n5th\n'

    def test_two_blank_lines(self, fp_with_two_blank_lines):
        paragraph = read_until_blank_line(fp_with_two_blank_lines)
        assert paragraph == '1st\n2nd\n3rd\n'
        second_paragraph = read_until_blank_line(fp_with_two_blank_lines)
        assert second_paragraph == '4th\n5th\n'
        rest = read_until_blank_line(fp_with_two_blank_lines)
        assert rest == '6th\n7th\n'

    def test_no_blank_line(self, fp_without_any_blank_line):
        paragraph = read_until_blank_line(fp_without_any_blank_line)
        assert paragraph == '1st\n2nd\n3rd\n'
        rest = fp_without_any_blank_line.read()
        assert rest == ''


class TestVerbsMatch(object):
    def test_with_trailing_e(self):
        assert verbs_match('Examine', 'examined')
        assert verbs_match('Analyze', 'analyzed')

    def test_without_trailing_e(self):
        assert verbs_match('Join', 'joined')

    def test_double_consonant(self):
        assert verbs_match('Stop', 'stopped')
        assert verbs_match('Scan', 'scanned')

    def test_special_case(self):
        # 'added' has a double consonant, but its present form ends with a
        # double consonant as well.
        assert verbs_match('Add', 'added')
