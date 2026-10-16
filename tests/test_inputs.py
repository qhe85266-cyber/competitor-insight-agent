"""Input checks never invoke research."""
import unittest
from app import validate_inputs


class InputsTest(unittest.TestCase):
    def test_rejected_inputs(self):
        for topic, names in [('  ', 'A,B'), ('topic', 'A'), ('topic', 'A,B,C,D'),
                             ('topic', 'A,a'), ('topic', 'Ａ,A'), ('topic', 'A, A')]:
            with self.subTest(topic=topic, names=names), self.assertRaises(ValueError):
                validate_inputs(topic, names)

    def test_two_and_three(self):
        for raw, expected in [(' A， B ', ['A', 'B']), ('A、B；C', ['A', 'B', 'C']),
                              ('A\nB;', ['A', 'B'])]:
            with self.subTest(raw=raw):
                self.assertEqual(validate_inputs(' topic ', raw), ('topic', expected))
