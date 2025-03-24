import unittest
from scrsit.core.document.ordered_list import OrderedList

class TestOrderedList(unittest.TestCase):
    def test_ordered_list_creation(self):
        ol = OrderedList([1, 2, 3])
        self.assertEqual(list(ol), [1, 2, 3])

    def test_ordered_list_append(self):
        ol = OrderedList()
        ol.append(1)
        self.assertEqual(list(ol), [1])

    def test_ordered_list_extend(self):
        ol = OrderedList()
        ol.extend([1, 2])
        self.assertEqual(list(ol), [1, 2])