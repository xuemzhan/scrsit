import unittest
from scrsit.core.document.base.structured_content import StructuredContent, OrderedList

class TestStructuredContent(unittest.TestCase):
    def test_structured_content_creation(self):
        content = StructuredContent(id="1", content="Test Content", level=1)
        self.assertEqual(content.id, "1")
        self.assertEqual(content.content, "Test Content")
        self.assertEqual(content.level, 1)
        self.assertIsNone(content.parent)
        self.assertEqual(len(content.children), 0)

    def test_get_catalogue(self):
        root = StructuredContent(id="root")
        level1_1 = StructuredContent(id="1.1", content="Level 1 - 1", level=1, parent=root)
        level1_2 = StructuredContent(id="1.2", content="Level 1 - 2", level=1, parent=root)
        level2_1 = StructuredContent(id="2.1", content="Level 2 - 1", level=2, parent=level1_1)
        root.children.extend([level1_1, level1_2])
        level1_1.children.append(level2_1)

        catalogue_level1 = root.get_catalogue(1)
        self.assertEqual(len(catalogue_level1), 2)
        self.assertIn({"id": "1.1", "content": "Level 1 - 1"}, catalogue_level1)
        self.assertIn({"id": "1.2", "content": "Level 1 - 2"}, catalogue_level1)

    def test_get_content_by_catalogue(self):
        root = StructuredContent(id="root")
        level1_1 = StructuredContent(id="1.1", content="Level 1 - 1", level=1, parent=root)
        root.children.append(level1_1)
        content = root.get_content_by_catalogue("1.1")
        self.assertEqual(content, "Level 1 - 1")
        self.assertIsNone(root.get_content_by_catalogue("non_existent"))