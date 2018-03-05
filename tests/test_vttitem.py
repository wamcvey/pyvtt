#!/usr/bin/env python
from codecs import encode as cencode
from os.path import abspath, dirname, join
from re import compile
from sys import path
from unittest import main, TestCase

from pyvtt import WebVTTItem, WebVTTTime, InvalidItem
from pyvtt.compat import str, basestring, is_py3

path.insert(0, abspath(join(dirname(__file__), '..')))


class TestAttributes(TestCase):

    def setUp(self):
        self.item = WebVTTItem()

    def test_has_id(self):
        self.assertTrue(hasattr(self.item, 'index'))
        self.assertTrue(isinstance(self.item.index, int))

    def test_has_content(self):
        self.assertTrue(hasattr(self.item, 'text'))
        self.assertTrue(isinstance(self.item.text, basestring))

    def test_has_start(self):
        self.assertTrue(hasattr(self.item, 'start'))
        self.assertTrue(isinstance(self.item.start, WebVTTTime))

    def test_has_end(self):
        self.assertTrue(hasattr(self.item, 'end'))
        self.assertTrue(isinstance(self.item.end, WebVTTTime))


class TestDuration(TestCase):

    def setUp(self):
        self.item = WebVTTItem(1, text='Hello world !')
        self.item.shift(minutes=1)
        self.item.end.shift(seconds=20)

    def test_duration(self):
        self.assertEqual(self.item.duration, (0, 0, 20, 0))


class TestCPS(TestCase):

    def setUp(self):
        self.item = WebVTTItem(1, text='Hello world !')
        self.item.shift(minutes=1)
        self.item.end.shift(seconds=20)

    def test_characters_per_second(self):
        self.assertEqual(self.item.characters_per_second, 0.65)

    def test_text_change(self):
        self.item.text = 'Hello world !\nHello world again !'
        self.assertEqual(self.item.characters_per_second, 1.6)

    def test_zero_duration(self):
        self.item.start.shift(seconds=20)
        self.assertEqual(self.item.characters_per_second, 0.0)

    def test_tags(self):
        self.item.text = '<b>bold</b>, <i>italic</i>, <u>underlined</u>\n' + \
                         '<font color="#ff0000">red text</font>' + \
                         ', <b>one,<i> two,<u> three</u></i></b>'
        self.assertEqual(self.item.characters_per_second, 2.45)


class TestTagRemoval(TestCase):

    def setUp(self):
        self.item = WebVTTItem(1, text='Hello world !')
        self.item.shift(minutes=1)
        self.item.end.shift(seconds=20)

    def test_italics_tag(self):
        self.item.text = '<i>Hello world !</i>'
        self.assertEqual(self.item.text_without_tags, 'Hello world !')

    def test_bold_tag(self):
        self.item.text = '<b>Hello world !</b>'
        self.assertEqual(self.item.text_without_tags, 'Hello world !')

    def test_underline_tag(self):
        self.item.text = '<u>Hello world !</u>'
        self.assertEqual(self.item.text_without_tags, 'Hello world !')

    def test_color_tag(self):
        self.item.text = '<font color="#ff0000">Hello world !</font>'
        self.assertEqual(self.item.text_without_tags, 'Hello world !')

    def test_tag_as_text(self):
        self.item.text = '<This is not a tag>'
        self.assertEqual(self.item.text_without_tags, 'This is not a tag')

    def test_split_tag_as_text(self):
        self.item.text = '<This is\n not a tag>'
        self.assertEqual(self.item.text_without_tags, 'This is\n not a tag')

    def test_all_tags(self):
        self.item.text = '<b>Bold</b>, <i>italic</i>, <u>underlined</u>\n' + \
                         '<font color="#ff0000">red text</font>' + \
                         ', <b>one,<i> two,<u> three</u></i></b>.'
        self.assertEqual(
            self.item.text_without_tags,
            'Bold, italic, underlined\nred text, one, two, three.')

    def test_bracket_tag(self):
        self.item.text = '[b]Hello world ![/b]'
        self.assertEqual(self.item.text_without_brackets, 'Hello world !')

    def test_key_tag(self):
        self.item.text = '{b}Hello world !{/b}'
        self.assertEqual(self.item.text_without_keys, 'Hello world !')

    def test_replacements(self):
        self.item.text = 'P & G, A + B'
        self.assertEqual(
            self.item.text_with_replacements([('&', 'and'), ('+', 'plus')]),
            'P and G, A plus B')

    def test_regex_eplacements(self):
        self.item.text = '\\tag21 This is a test!'
        self.assertEqual(
            self.item.text_with_replacements([(compile(r'\\tag\d+ '), '')]),
            'This is a test!')


class TestShifting(TestCase):

    def setUp(self):
        self.item = WebVTTItem(1, text='Hello world !')
        self.item.shift(minutes=1)
        self.item.end.shift(seconds=20)

    def test_shift_up(self):
        self.item.shift(1, 2, 3, 4)
        self.assertEqual(self.item.start, (1, 3, 3, 4))
        self.assertEqual(self.item.end, (1, 3, 23, 4))
        self.assertEqual(self.item.duration, (0, 0, 20, 0))
        self.assertEqual(self.item.characters_per_second, 0.65)

    def test_shift_down(self):
        self.item.shift(5)
        self.item.shift(-1, -2, -3, -4)
        self.assertEqual(self.item.start, (3, 58, 56, 996))
        self.assertEqual(self.item.end, (3, 59, 16, 996))
        self.assertEqual(self.item.duration, (0, 0, 20, 0))
        self.assertEqual(self.item.characters_per_second, 0.65)

    def test_shift_by_ratio(self):
        self.item.shift(ratio=2)
        self.assertEqual(self.item.start, {'minutes': 2})
        self.assertEqual(self.item.end, {'minutes': 2, 'seconds': 40})
        self.assertEqual(self.item.duration, (0, 0, 40, 0))
        self.assertEqual(self.item.characters_per_second, 0.325)


class TestOperators(TestCase):

    def setUp(self):
        self.item = WebVTTItem(1, text='Hello world!')
        self.item.shift(minutes=1)
        self.item.end.shift(seconds=20)

    def test_cmp(self):
        self.assertEqual(self.item, self.item)


class TestSerialAndParsing(TestCase):

    def setUp(self):
        self.item = WebVTTItem(1, text="Hello world !")
        self.item.shift(minutes=1)
        self.item.end.shift(seconds=20)
        self.string = '1\n00:01:00.000 --> 00:01:20.000\nHello world !\n'
        self.bad_string = 'foobar'
        self.coordinates = ('1\n00:01:00.000 --> 00:01:20.000 X1:000 X2:000 '
                            'Y1:050 Y2:100\nHello world !\n')
        self.vtt = ('00:01:00.000 --> 00:01:20.000 D:vertical A:start '
                    'L:12%\nHello world !\n')
        self.string_index = 'foo\n00:01:00.000 --> 00:01:20.000\nHello !\n'
        self.dots = '1\n00:01:00.000 --> 00:01:20.000\nHello world !\n'
        self.no_index = '00:01:00,000 --> 00:01:20,000\nHello world !\n'
        self.junk_after_timestamp = ('1\n00:01:00,000 --> 00:01:20,000?\n'
                                     'Hello world !\n')

    def test_serialization(self):
        self.assertEqual(str(self.item), self.string[2:])

    def test_from_string(self):
        self.assertEqual(WebVTTItem.from_string(self.string), self.item)
        self.assertRaises(InvalidItem, WebVTTItem.from_string, self.bad_string)

    def test_coordinates(self):
        item = WebVTTItem.from_string(self.coordinates)
        self.assertEqual(item, self.item)
        self.assertEqual(item.position, 'X1:000 X2:000 Y1:050 Y2:100')

    def test_vtt_positioning(self):
        vtt = WebVTTItem.from_string(self.vtt)
        self.assertEqual(vtt.position, 'D:vertical A:start L:12%')
        self.assertEqual(vtt.index, None)
        self.assertEqual(vtt.text, 'Hello world !')

    def test_idempotence(self):
        vtt = WebVTTItem.from_string(self.vtt)
        self.assertEqual(str(vtt), self.vtt)
        item = WebVTTItem.from_string(self.coordinates)
        self.assertEqual(str(item), self.coordinates[2:])

    def test_dots(self):
        self.assertEqual(WebVTTItem.from_string(self.dots), self.item)

    # Bug reported in https://github.com/byroot/pysrt/issues/16
    def test_paring_error(self):
        self.assertRaises(
            InvalidItem, WebVTTItem.from_string, '1\n'
            '00:01:00,000 -> 00:01:20,000 X1:000 X2:000 '
            'Y1:050 Y2:100\nHello world !\n')

    def test_string_index(self):
        item = WebVTTItem.from_string(self.string_index)
        self.assertEqual(item.index, 'foo')
        self.assertEqual(item.text, 'Hello !')

    def test_no_index(self):
        item = WebVTTItem.from_string(self.no_index)
        self.assertEqual(item.index, None)
        self.assertEqual(item.text, 'Hello world !')

    def test_junk_after_timestamp(self):
        item = WebVTTItem.from_string(self.junk_after_timestamp)
        self.assertEqual(item, self.item)

    def test_is_unicode(self):
        # This tests makes no sense for Py3
        if is_py3:
            return
        # Defining non_unicode encodings list as defined in
        # https://docs.python.org/2/library/codecs.html#standard-encodings
        non_unicode_encodings = [
            'big5', 'big5hkscs', 'cp1250', 'cp1251', 'cp1252', 'cp1253',
            'cp1254', 'cp1255', 'cp1256', 'cp1257', 'cp1258',
            'euc_jp', 'euc_jis_2004', 'euc_jisx0213', 'euc_kr',
            'gb2312', 'gbk', 'gb18030', 'hz', 'iso2022_jp',
            'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_2004',
            'iso2022_jp_3', 'iso2022_jp_ext', 'iso2022_kr',
            'latin_1', 'iso8859_2', 'iso8859_3', 'iso8859_4',
            'iso8859_5', 'iso8859_6', 'iso8859_7', 'iso8859_8',
            'iso8859_9', 'iso8859_10', 'iso8859_11', 'iso8859_13',
            'iso8859_13', 'iso8859_14', 'iso8859_15', 'iso8859_16',
            'johab', 'koi8_r', 'koi8_u', 'mac_cyrillic', 'mac_greek',
            'mac_iceland', 'mac_latin2', 'mac_roman', 'mac_turkish',
            'ptcp154', 'shift_jis', 'shift_jis_2004', 'shift_jisx0213']
        for enc in non_unicode_encodings:
            non_unicode = cencode('non_unicode\n', enc)
            self.no_unicode_item = WebVTTItem(1, text=non_unicode)
            self.assertRaises(NotImplementedError, WebVTTItem.__str__,
                              self.no_unicode_item)


if __name__ == '__main__':
    main()
