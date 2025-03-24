import unittest
from scrsit.core.document.base.entity import Entity

class TestEntity(unittest.TestCase):
    def test_entity_creation(self):
        entity = Entity(id="ent1", name="Test Entity", type="GENERIC")
        self.assertEqual(entity.id, "ent1")
        self.assertEqual(entity.name, "Test Entity")
        self.assertEqual(entity.type, "GENERIC")