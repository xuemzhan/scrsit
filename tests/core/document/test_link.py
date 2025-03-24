import unittest
from scrsit.core.document.link import Link

class TestLink(unittest.TestCase):
    def test_link_creation(self):
        link = Link(target="http://example.com", summary="Example Link")
        self.assertEqual(link.target, "http://example.com")
        self.assertEqual(link.summary, "Example Link")