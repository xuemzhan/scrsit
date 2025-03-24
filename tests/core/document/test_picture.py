import unittest
from scrsit.core.document.picture import Picture

class TestPicture(unittest.TestCase):
    def test_picture_creation(self):
        picture = Picture(id="pic1", doc_id="doc1", name="image.png")
        self.assertEqual(picture.id, "pic1")
        self.assertEqual(picture.doc_id, "doc1")
        self.assertEqual(picture.name, "image.png")