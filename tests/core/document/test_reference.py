import unittest
from scrsit.core.document.reference import Reference

class TestReference(unittest.TestCase):
    def test_reference_creation(self):
        reference = Reference(authors=["Author 1"], publisher="Publisher A")
        self.assertEqual(reference.authors, ["Author 1"])
        self.assertEqual(reference.publisher, "Publisher A")