#!/usr/bin/env python
from datetime import time
from os.path import abspath, dirname, join
from random import choice, uniform
from sys import maxsize
from sys import path
from unittest import main, TestCase

from pyvtt import WebVTTTime, InvalidTimeString

path.insert(0, abspath(join(dirname(__file__), '..')))


class TestSimpleTime(TestCase):

    def setUp(self):
        self.time = WebVTTTime()

    def test_default_value(self):
        self.assertEqual(self.time.ordinal, 0)

    def test_micro_seconds(self):
        self.time.milliseconds = 1
        self.assertEqual(self.time.milliseconds, 1)
        self.time.hours += 42
        self.assertEqual(self.time.milliseconds, 1)
        self.time.milliseconds += 1000
        self.assertEqual(self.time.seconds, 1)

    def test_seconds(self):
        self.time.seconds = 1
        self.assertEqual(self.time.seconds, 1)
        self.time.hours += 42
        self.assertEqual(self.time.seconds, 1)
        self.time.seconds += 60
        self.assertEqual(self.time.minutes, 1)

    def test_minutes(self):
        self.time.minutes = 1
        self.assertEqual(self.time.minutes, 1)
        self.time.hours += 42
        self.assertEqual(self.time.minutes, 1)
        self.time.minutes += 60
        self.assertEqual(self.time.hours, 43)

    def test_hours(self):
        self.time.hours = 1
        self.assertEqual(self.time.hours, 1)
        self.time.minutes += 42
        self.assertEqual(self.time.hours, 1)

    def test_shifting_forward(self):
        self.time.shift(1, 1, 1, 1)
        self.assertEqual(self.time, (1, 1, 1, 1))

    def test_shifting_backwards(self):
        self.time.shift(-1, -1, -1, -1)
        self.assertEqual(self.time, (-2, 58, 58, 999))
        self.time = WebVTTTime(1, 2, 3, 4)
        self.time.shift(-1, -1, -1, -1)
        self.assertEqual(self.time, (0, 1, 2, 3))

    def test_descriptor_from_class(self):
        self.assertRaises(AttributeError, lambda: WebVTTTime.hours)


class TestTimeParsing(TestCase):
    KNOWN_VALUES = (
        ('00:00:00.000', (0, 0, 0, 0)),
        ('00:00:00.001', (0, 0, 0, 1)),
        ('00:00:02.000', (0, 0, 2, 0)),
        ('00:03:00.000', (0, 3, 0, 0)),
        ('04:00:00.000', (4, 0, 0, 0)),
        ('12:34:56.789', (12, 34, 56, 789)),
    )

    def test_parsing(self):
        for time_string, time_items in self.KNOWN_VALUES:
            self.assertEqual(time_string, WebVTTTime(*time_items))

    def test_serialization(self):
        for time_string, time_items in self.KNOWN_VALUES:
            self.assertEqual(time_string, str(WebVTTTime(*time_items)))

    def test_negative_serialization(self):
        self.assertEqual('00:00:00.000', str(WebVTTTime(-1, 2, 3, 4)))
        self.assertEqual('00:00:00.000',
                         str(WebVTTTime(-maxsize, 2, 3, 4)))
        self.assertEqual('00:00:00.000', str(WebVTTTime(0, -2, 3, 4)))
        self.assertEqual('00:00:00.000', str(WebVTTTime(0, 0, -3, 4)))
        self.assertEqual('00:00:00.000', str(WebVTTTime(0, 0, 0, -4)))

    def test_invalid_time_string(self):
        self.assertRaises(InvalidTimeString, WebVTTTime.from_string, 'test')

    def test_invalid_int(self):
        random_long = int(choice(list(range(0, 10000000))))
        # String
        self.assertRaises(ValueError, lambda: WebVTTTime.parse_int('test'))
        # Binary
        self.assertRaises(ValueError, lambda: WebVTTTime.parse_int(bin(42)))
        # Char
        self.assertRaises(ValueError, lambda: WebVTTTime.parse_int('t'))
        # None
        self.assertRaises(TypeError, WebVTTTime.parse_int)
        # None
        self.assertRaises(TypeError, WebVTTTime.parse_int(None))
        # List
        self.assertRaises(TypeError, WebVTTTime.parse_int(list(range(10))))
        # Tuple
        self.assertRaises(TypeError, WebVTTTime.parse_int((1, 1)))
        # Boolean
        self.assertRaises(TypeError, WebVTTTime.parse_int(True))
        # Float
        self.assertRaises(TypeError, WebVTTTime.parse_int(uniform(1, 100)))
        # Complex
        self.assertRaises(TypeError, WebVTTTime.parse_int(1j))
        # Long
        self.assertRaises(TypeError, WebVTTTime.parse_int(random_long))
        # Dictionary
        self.assertRaises(TypeError,
                          WebVTTTime.parse_int({'Test1': 1, 'Test0': 0}))

    def test_max_values(self):
        self.assertEqual('99:59:59.999', str(WebVTTTime(99, 59, 59, 999)))
        self.assertEqual('100:40:39.999', str(WebVTTTime(99, 99, 99, 999)))


class TestCoercing(TestCase):

    def test_from_tuple(self):
        self.assertEqual((0, 0, 0, 0), WebVTTTime())
        self.assertEqual((0, 0, 0, 1), WebVTTTime(milliseconds=1))
        self.assertEqual((0, 0, 2, 0), WebVTTTime(seconds=2))
        self.assertEqual((0, 3, 0, 0), WebVTTTime(minutes=3))
        self.assertEqual((4, 0, 0, 0), WebVTTTime(hours=4))
        self.assertEqual((1, 2, 3, 4), WebVTTTime(1, 2, 3, 4))

    def test_from_dict(self):
        self.assertEqual(dict(), WebVTTTime())
        self.assertEqual(dict(milliseconds=1), WebVTTTime(milliseconds=1))
        self.assertEqual(dict(seconds=2), WebVTTTime(seconds=2))
        self.assertEqual(dict(minutes=3), WebVTTTime(minutes=3))
        self.assertEqual(dict(hours=4), WebVTTTime(hours=4))
        self.assertEqual(dict(hours=1, minutes=2, seconds=3, milliseconds=4),
                         WebVTTTime(1, 2, 3, 4))

    def test_from_time(self):
        time_obj = time(1, 2, 3, 4000)
        self.assertEqual(WebVTTTime(1, 2, 3, 4), time_obj)
        self.assertTrue(WebVTTTime(1, 2, 3, 5) >= time_obj)
        self.assertTrue(WebVTTTime(1, 2, 3, 3) <= time_obj)
        self.assertTrue(WebVTTTime(1, 2, 3, 0) != time_obj)
        self.assertEqual(WebVTTTime(1, 2, 3, 4).to_time(), time_obj)
        self.assertTrue(WebVTTTime(1, 2, 3, 5).to_time() >= time_obj)
        self.assertTrue(WebVTTTime(1, 2, 3, 3).to_time() <= time_obj)
        self.assertTrue(WebVTTTime(1, 2, 3, 0).to_time() != time_obj)

    def test_from_ordinal(self):
        self.assertEqual(WebVTTTime.from_ordinal(3600000), {'hours': 1})
        self.assertEqual(WebVTTTime(1), 3600000)

    def test_from_repr(self):
        self.time = WebVTTTime()
        self.assertEqual('WebVTTTime(0, 0, 0, 0)', self.time.__repr__())
        self.time = WebVTTTime(1, 1, 1, 1)
        self.assertEqual('WebVTTTime(1, 1, 1, 1)', self.time.__repr__())


class TestOperators(TestCase):

    def setUp(self):
        self.time = WebVTTTime(1, 2, 3, 4)

    def test_add(self):
        self.assertEqual(self.time + (1, 2, 3, 4), (2, 4, 6, 8))

    def test_iadd(self):
        self.time += (1, 2, 3, 4)
        self.assertEqual(self.time, (2, 4, 6, 8))

    def test_sub(self):
        self.assertEqual(self.time - (1, 2, 3, 4), 0)

    def test_isub(self):
        self.time -= (1, 2, 3, 4)
        self.assertEqual(self.time, 0)

    def test_mul(self):
        self.assertEqual(self.time * 2, WebVTTTime(2, 4, 6, 8))
        self.assertEqual(self.time * 0.5,  (0, 31, 1, 502))

    def test_imul(self):
        self.time *= 2
        self.assertEqual(self.time,  (2, 4, 6, 8))
        self.time *= 0.5
        self.assertEqual(self.time, (1, 2, 3, 4))


if __name__ == '__main__':
    main()
