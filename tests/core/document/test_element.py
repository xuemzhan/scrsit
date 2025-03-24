import unittest
from scrsit.core.document.element import Element

class TestElement(unittest.TestCase):
    def test_element_creation(self):
        element = Element(id="elem1", doc_id="doc1", name="Section Title", content="Section Content")
        self.assertEqual(element.id, "elem1")
        self.assertEqual(element.doc_id, "doc1")
        self.assertEqual(element.name, "Section Title")