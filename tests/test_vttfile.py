#!/usr/bin/env python
# -*- coding: utf-8 -*-
from codecs import open as copen
from os import linesep, remove
from os.path import abspath, dirname, join
from random import randint, shuffle
from sys import path
from unittest import main, TestCase

from pyvtt import (from_string, open as vttopen, Error as vttError, stream,
                   WebVTTFile, WebVTTItem)
from pyvtt.compat import str, open
from pyvtt.vttexc import InvalidFile

file_path = join(dirname(__file__), '..')
path.insert(0, abspath(file_path))


class TestOpen(TestCase):

    def setUp(self):
        self.static_path = join(file_path, 'tests', 'static')
        self.utf8_path = join(self.static_path, 'utf-8.vtt')
        self.windows_path = join(self.static_path, 'windows-1252.srt')
        self.invalid_path = join(self.static_path, 'invalid.srt')

    def test_utf8(self):
        self.assertEqual(len(vttopen(self.utf8_path)), 1332)
        self.assertEqual(vttopen(self.utf8_path).encoding, 'utf_8')
        self.assertRaises(UnicodeDecodeError, vttopen, self.windows_path)

    def test_windows1252(self):
        vtt_file = vttopen(self.windows_path, encoding='windows-1252')
        self.assertEqual(len(vtt_file), 1332)
        self.assertEqual(vtt_file.eol, '\r\n')
        self.assertRaises(UnicodeDecodeError, vttopen, self.utf8_path, 
                          encoding='ascii')

    def test_error_handling(self):
        self.assertRaises(vttError, vttopen, self.invalid_path,
                          error_handling=WebVTTFile.ERROR_RAISE)
        self.assertRaises(vttError, vttopen, self.invalid_path,
                          error_handling=WebVTTFile.ERROR_LOG)


class TestFromString(TestCase):

    def setUp(self):
        self.static_path = join(file_path, 'tests', 'static')
        self.utf8_path = join(self.static_path, 'utf-8.vtt')
        self.windows_path = join(self.static_path, 'windows-1252.srt')
        self.invalid_path = join(self.static_path, 'invalid.srt')
        self.temp_path = join(self.static_path, 'temp.srt')

    def test_utf8(self):
        unicode_content = copen(self.utf8_path, encoding='utf_8').read()
        self.assertEqual(len(from_string(unicode_content)), 1332)
        self.assertRaises(UnicodeDecodeError, open(self.windows_path).read)

    def test_windows1252(self):
        vtt_string = copen(self.windows_path, encoding='windows-1252').read()
        vtt_file = from_string(vtt_string, encoding='windows-1252', eol='\r\n')
        self.assertEqual(len(vtt_file), 1332)
        self.assertEqual(vtt_file.eol, '\r\n')
        self.assertRaises(UnicodeDecodeError, vttopen,
                          self.utf8_path, encoding='ascii')


class TestCompareWithReference(TestCase):

    def setUp(self):
        self.static_path = join(file_path, 'tests', 'vtt_test')
        self.ref_path = join(self.static_path, 'ref.vtt')
        self.ref_dur_shifted_path = join(
            self.static_path, 'ref_duration_shifted.vtt')
        self.ref_dur_sliced_path = join(
            self.static_path, 'ref_duration_sliced.vtt')
        self.test_tags_path = join(self.static_path, 'test_tags.vtt')
        self.test_keys_path = join(self.static_path, 'test_keys.vtt')
        self.test_trailings_path = join(
            self.static_path, 'test_trailings.vtt')
        self.test_duration_path = join(
            self.static_path, 'test_duration.vtt')
        self.test_replacements_path = join(
            self.static_path, 'test_replacements.vtt')
        # Reference file (clean, no tags/keys)
        self.vtt_file_ref = vttopen(self.ref_path, encoding='utf_8')

    def test_compare_tags_with_ref(self):
        vtt_file_ut = vttopen(self.test_tags_path, encoding='utf_8')
        # Only tags removal is enabled.
        vtt_file_ut.clean_text(tags=True, keys=False, trailing=False)
        self.assertEqual(self.vtt_file_ref.text, vtt_file_ut.text)

    def test_compare_keys_with_ref(self):
        vtt_file_ut = vttopen(self.test_keys_path, encoding='utf_8')
        # Only keys removal is enabled.
        vtt_file_ut.clean_text(tags=False, keys=True, trailing=False)
        self.assertEqual(self.vtt_file_ref.text, vtt_file_ut.text)

    def test_compare_trailings_with_ref(self):
        ref_path2 = join(self.static_path, 'ref_notrailings.vtt')
        # Reference file (clean, no whitespaces).
        vtt_file_ref2 = vttopen(ref_path2, encoding='utf_8')

        # Only trailing removal (whitespaces at end(beginning) is enabled.
        vtt_file_ut = vttopen(self.test_trailings_path, encoding='utf_8')
        vtt_file_ut.clean_text(tags=False, keys=False, trailing=True)
        self.assertEqual(vtt_file_ref2.text, vtt_file_ut.text)

    def test_compare_replacements_with_ref(self):
        ref_path2 = join(self.static_path, 'ref_replacements.vtt')
        # Reference file (clean, no whitespaces).
        vtt_file_ref2 = vttopen(ref_path2, encoding='utf_8')

        vtt_file_ut = vttopen(self.test_replacements_path, encoding='utf_8')
        # Only & -> and replacement
        vtt_file_ut.apply_replacements(replacements=[('&', 'and'),
                                                     ('+', 'plus')])
        self.assertEqual(vtt_file_ref2.text, vtt_file_ut.text)

    def test_compare_shift_with_ref(self):
        vtt_file_ref = vttopen(self.ref_dur_shifted_path, encoding='utf_8')
        vtt_file_ut1 = vttopen(self.test_duration_path, encoding='utf_8')
        vtt_file_ut2 = vttopen(self.test_duration_path, encoding='utf_8')
        ref_ratio_path = join(
            self.static_path, 'ref_duration_ratio.vtt')
        vtt_file_ref_ratio = vttopen(ref_ratio_path, encoding='utf_8')

        # Shifted 5 hours, 5 minutes, 5 seconds, 500 milliseconds.
        vtt_file_ut1.shift(hours=5, minutes=5, seconds=5, milliseconds=500)
        self.assertEqual(vtt_file_ut1, vtt_file_ref)

        # Shifted BACK 5 hours, 5 minutes, 5 seconds, 500 milliseconds.
        vtt_file_ut1.shift(hours=-5, minutes=-5, seconds=-5, milliseconds=-500)

        self.assertEqual(vtt_file_ut1, vtt_file_ut2)
        vtt_file_ut1.shift(ratio=2)
        # Shifted with a ratio of 2.
        self.assertEqual(vtt_file_ut1, vtt_file_ref_ratio)

    def test_compare_slice_with_ref(self):
        vtt_file_ref = vttopen(self.ref_dur_sliced_path, encoding='utf_8')
        vtt_file_source = vttopen(self.test_duration_path, encoding='utf_8')
        temp_file_path = join(self.static_path, 'temp_test.vtt')

        vtt_file_ut = vtt_file_source.slice(starts_after={'minutes': 2})
        self.assertRaises(InvalidFile, vtt_file_ut.save, temp_file_path)
        remove(temp_file_path)

        vtt_file_ut = vtt_file_source.slice(
            starts_after={'seconds': 20}, ends_before={'seconds': 42})
        vtt_file_ut.save(temp_file_path, eol='\n', encoding='utf_8')
        self.assertEqual(vtt_file_ut, vtt_file_ref)
        remove(temp_file_path)

        vtt_file_ut = vtt_file_source.slice(
            starts_after={'seconds': -20}, ends_before={'seconds': -42})
        self.assertRaises(InvalidFile, vtt_file_ut.save, temp_file_path)
        remove(temp_file_path)

        # ends_before > ends_after
        vtt_file_ut = vtt_file_source.slice(
            ends_before={'seconds': 42}, ends_after={'seconds': 40})

        self.assertRaises(InvalidFile, vtt_file_ut.save, temp_file_path)
        remove(temp_file_path)

        # starts_before < starts_after
        vtt_file_ut = vtt_file_source.slice(
            starts_before={'seconds': 10}, starts_after={'seconds': 30})

        self.assertRaises(InvalidFile, vtt_file_ut.save, temp_file_path)
        remove(temp_file_path)

        # starts_after > ends_before
        vtt_file_ut = vtt_file_source.slice(
            starts_after={'seconds': 42}, ends_before={'seconds': 30})

        self.assertRaises(InvalidFile, vtt_file_ut.save, temp_file_path)
        remove(temp_file_path)


class TestSerialization(TestCase):

    def setUp(self):
        self.static_path = join(file_path, 'tests', 'static')
        self.utf8_path = join(self.static_path, 'utf-8.vtt')
        self.windows_path = join(self.static_path, 'windows-1252.srt')
        self.invalid_path = join(self.static_path, 'invalid.srt')
        self.temp_path = join(self.static_path, 'temp.srt')

    def test_compare_from_string_and_from_path(self):
        unicode_content = copen(self.utf8_path, encoding='utf_8').read()
        iterator = list(zip(vttopen(self.utf8_path),
                            from_string(unicode_content)))
        for file_item, string_item in iterator:
            self.assertEqual(str(file_item), str(string_item))

    def test_save_new_eol_and_encoding(self):
        vtt_file = vttopen(self.windows_path, encoding='windows-1252')
        vtt_file.save(self.temp_path, eol='\n', encoding='utf-8')
        self.assertEqual(bytes(open(self.temp_path, 'rb').read()),
                         bytes(open(self.utf8_path, 'rb').read()))
        remove(self.temp_path)

    def test_save_empty_slice(self):
        vtt_file = vttopen(self.windows_path, encoding='windows-1252')
        sliced_file = vtt_file.slice(starts_after=(0, 0, 0, 0),
                                     ends_before=(0, 0, 0, 0))
        self.assertEqual(len(sliced_file), 0)
        self.assertRaises(InvalidFile, sliced_file.save, self.temp_path)

    def test_save_overwrite(self):
        overwrite_source_path1 = join(
            file_path, 'tests', 'vtt_test', 'overwrite_source1.vtt')
        overwrite_source_path2 = join(
            file_path, 'tests', 'vtt_test', 'overwrite_source2.vtt')
        overwrite_target_path = join(
            file_path, 'tests', 'vtt_test', 'overwrite_target.vtt')

        vtt_file1 = vttopen(overwrite_source_path1, encoding='utf-8')
        vtt_file1.save(overwrite_target_path, eol=vtt_file1._eol,
                       encoding=vtt_file1.encoding)
        self.assertEqual(bytes(open(overwrite_source_path1, 'rb').read()),
                         bytes(open(overwrite_target_path, 'rb').read()))

        vtt_file2 = vttopen(overwrite_source_path2, encoding='utf-8')
        vtt_file2.save(overwrite_target_path, eol=vtt_file2._eol,
                       encoding=vtt_file2.encoding)
        self.assertEqual(bytes(open(overwrite_source_path2, 'rb').read()),
                         bytes(open(overwrite_target_path, 'rb').read()))

        remove(overwrite_target_path)

    def test_save_with_indexes(self):
        file = vttopen(join(self.static_path, 'no-indexes.srt'))
        file.clean_indexes()
        file_with_indexes = join(
            file_path, 'tests', 'vtt_test', 'file_with_indexes.vtt')
        file_with_indexes_target_path = join(
            file_path, 'tests', 'vtt_test', 'file_with_indexes_target.vtt')
        file.save(file_with_indexes_target_path, include_indexes=True)
        self.assertEqual(
            bytes(open(file_with_indexes, 'rb').read()),
            bytes(open(file_with_indexes_target_path, 'rb').read()))
        remove(file_with_indexes_target_path)

    def test_eol_convertion(self):

        self.temp_eol_path = join(
            self.static_path, 'temp_eol_conv.vtt')
        end_of_lines = ['\n', '\r', '\r\n']
        enc = 'utf-8'

        for eols in end_of_lines:
            input_eol = open(self.temp_eol_path, 'wb')
            input_eol.write(
                "00:01:00,000 --> 00:02:00,000"
                " {0} TestEOLConvertion + {0}".format(eols).encode())
            input_eol.close()

            input_file = open(self.temp_eol_path, 'rU', encoding=enc)
            input_file.read()
            self.assertEqual(input_file.newlines, eols)

            vtt_file = vttopen(self.temp_eol_path, encoding=enc)
            vtt_file.save(self.temp_eol_path, eol='\n')

            output_file = open(self.temp_eol_path, 'rU', encoding=enc)
            output_file.read()
            self.assertEqual(output_file.newlines, '\n')

            remove(self.temp_eol_path)

    def test_eol_preservation(self):

        # Tests input eol is kept after saving

        self.temp_eol_path = join(
            self.static_path, 'temp_eol_preserv.vtt')
        end_of_lines = ['\n', '\r', '\r\n']
        enc = 'utf-8'

        for eols in end_of_lines:
            input_eol = open(self.temp_eol_path, 'wb')
            input_eol.write(
                "00:01:00,000 --> 00:02:00,000"
                " {0} TestEOLPreservation + {0}".format(eols).encode())
            input_eol.close()

            input_file = open(self.temp_eol_path, 'rU', encoding=enc)
            input_file.read()
            self.assertEqual(eols, input_file.newlines)

            vtt_file = vttopen(self.temp_eol_path, encoding=enc)
            vtt_file.save(self.temp_eol_path, eol=input_file.newlines)

            output_file = open(self.temp_eol_path, 'rU', encoding=enc)
            output_file.read()
            self.assertEqual(output_file.newlines, input_file.newlines)

            remove(self.temp_eol_path)


class TestSlice(TestCase):

    def setUp(self):
        self.file = vttopen(join(
            file_path, 'tests', 'static', 'utf-8.vtt'))

    def test_slice(self):
        self.assertEqual(len(self.file.slice(ends_before=(1, 2, 3, 4))), 872)
        self.assertEqual(len(self.file.slice(ends_after=(1, 2, 3, 4))), 460)
        self.assertEqual(len(self.file.slice(starts_before=(1, 2, 3, 4))), 873)
        self.assertEqual(len(self.file.slice(starts_after=(1, 2, 3, 4))), 459)

    def test_at(self):
        self.assertEqual(len(self.file.at((0, 0, 31, 0))), 1)
        self.assertEqual(len(self.file.at(seconds=31)), 1)


class TestShifting(TestCase):

    def test_shift(self):
        vtt_file = WebVTTFile([WebVTTItem()])
        vtt_file.shift(1, 1, 1, 1)
        self.assertEqual(vtt_file[0].end, (1, 1, 1, 1))
        vtt_file.shift(ratio=2)
        self.assertEqual(vtt_file[0].end, (2, 2, 2, 2))


class TestText(TestCase):

    def test_single_item(self):
        vtt_file = WebVTTFile([
            WebVTTItem(1, {'seconds': 1}, {'seconds': 2}, 'Hello')
        ])
        self.assertEqual(vtt_file.text, 'Hello')

    def test_multiple_item(self):
        vtt_file = WebVTTFile([
            WebVTTItem(1, {'seconds': 0}, {'seconds': 3}, 'Hello'),
            WebVTTItem(1, {'seconds': 1}, {'seconds': 2}, 'World !')
        ])
        self.assertEqual(vtt_file.text, 'Hello\nWorld !')


class TestDuckTyping(TestCase):

    def setUp(self):
        self.duck = WebVTTFile()

    def test_act_as_list(self):
        self.assertTrue(iter(self.duck))

        def iter_over_file():
            try:
                for _ in self.duck:
                    pass
            except Exception:
                return False
            return True
        self.assertTrue(iter_over_file())
        self.assertTrue(hasattr(self.duck, '__getitem__'))
        self.assertTrue(hasattr(self.duck, '__setitem__'))
        self.assertTrue(hasattr(self.duck, '__delitem__'))


class TestEOLProperty(TestCase):

    def setUp(self):
        self.file = WebVTTFile()

    def test_default_value(self):
        self.assertEqual(self.file.eol, linesep)
        vtt_file = WebVTTFile(eol='\r\n')
        self.assertEqual(vtt_file.eol, '\r\n')

    def test_set_eol(self):
        self.file.eol = '\r\n'
        self.assertEqual(self.file.eol, '\r\n')


class TestCleanIndexes(TestCase):

    def setUp(self):
        self.file = vttopen(join(file_path, 'tests', 'static', 'utf-8.vtt'))

    def test_clean_indexes(self):
        shuffle(self.file)
        for item in self.file:
            item.index = randint(0, 1000)
        self.file.clean_indexes()
        self.assertEqual([i.index for i in self.file],
                         list(range(1, len(self.file) + 1)))
        for first, second in zip(self.file[:-1], self.file[1:]):
            self.assertTrue(first <= second)


class TestBOM(TestCase):
    """
    In response of issue #6 https://github.com/byroot/pysrt/issues/6
    """

    def setUp(self):
        self.base_path = join(file_path, 'tests', 'static')

    def __test_encoding(self, encoding):
        vtt_file = vttopen(join(self.base_path, encoding))
        self.assertEqual(len(vtt_file), 7)
        self.assertEqual(vtt_file[0].index, 1)

    def test_utf8(self):
        self.__test_encoding('bom-utf-8.srt')

    def test_utf16le(self):
        self.__test_encoding('bom-utf-16-le.srt')

    def test_utf16be(self):
        self.__test_encoding('bom-utf-16-be.srt')

    def test_utf32le(self):
        self.__test_encoding('bom-utf-32-le.srt')

    def test_utf32be(self):
        self.__test_encoding('bom-utf-32-be.srt')


class TestIntegration(TestCase):
    """
    Test some borderlines features found on
    http://ale5000.altervista.org/subtitles.htm
    """

    def setUp(self):
        self.base_path = join(file_path, 'tests', 'static')

    def test_length(self):
        path = join(self.base_path, 'capability_tester.srt')
        file = vttopen(path)
        self.assertEqual(len(file), 37)

    def test_empty_file(self):
        self.assertRaises(InvalidFile, vttopen, '/dev/null',
                          error_handling=WebVTTFile.ERROR_RAISE)

    def test_blank_lines(self):
        items = list(stream(['\n'] * 20,
                            error_handling=WebVTTFile.ERROR_RAISE))
        self.assertEqual(len(items), 0)

    def test_missing_indexes(self):
        items = vttopen(join(self.base_path, 'no-indexes.srt'))
        self.assertEqual(len(items), 7)


if __name__ == '__main__':
    main()
