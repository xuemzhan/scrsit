import unittest
from scrsit.core.document.base.relationship import Relationship

class TestRelationship(unittest.TestCase):
    def test_relationship_creation(self):
        relation = Relationship(id="rel1", from_entity_id="ent1", to_entity_id="ent2")
        self.assertEqual(relation.id, "rel1")
        self.assertEqual(relation.from_entity_id, "ent1")
        self.assertEqual(relation.to_entity_id, "ent2")