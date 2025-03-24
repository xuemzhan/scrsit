import unittest
from scrsit.core.document.base.chunk import Chunk

class TestChunk(unittest.TestCase):
    def test_chunk_creation(self):
        chunk = Chunk(id="1", doc_id="doc1", order_index=0, content="Chunk Content", tokens=5)
        self.assertEqual(chunk.id, "1")
        self.assertEqual(chunk.doc_id, "doc1")
        self.assertEqual(chunk.order_index, 0)
        self.assertEqual(chunk.content, "Chunk Content")
        self.assertEqual(chunk.tokens, 5)
        self.assertIsNone(chunk.vectors)