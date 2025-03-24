import unittest
from scrsit.core.document.table import Table

class TestTable(unittest.TestCase):
    def test_table_creation(self):
        table = Table(order_index=0, content="Header|Value\n---|---")
        self.assertEqual(table.order_index, 0)
        self.assertEqual(table.content, "Header|Value\n---|---")