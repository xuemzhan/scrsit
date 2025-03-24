import unittest
from scrsit.core.document.formula import Formula

class TestFormula(unittest.TestCase):
    def test_formula_creation(self):
        formula = Formula(raw="E=mc^2")
        self.assertEqual(formula.raw, "E=mc^2")
        self.assertEqual(formula.get_formula(), "E=mc^2")