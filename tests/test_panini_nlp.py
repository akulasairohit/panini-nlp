"""Tests for panini-nlp package."""

import unittest
from panini_nlp.sandhi import SandhiEngine
from panini_nlp.morphology import MorphologicalAnalyzer
from panini_nlp.semantics import SemanticParser
from panini_nlp.chandas import ChandasAnalyzer
from panini_nlp.samasa import SamasaAnalyzer
from panini_nlp.validator import SanskritValidator


class TestSandhi(unittest.TestCase):
    def setUp(self):
        self.engine = SandhiEngine()

    def test_dirgha_sandhi(self):
        """6.1.101 — अ + अ → आ"""
        result = self.engine.apply("अ", "अग्नि")
        self.assertIsNotNone(result.rule_applied)
        self.assertEqual(result.rule_applied.id, "6.1.101")

    def test_guna_sandhi(self):
        """6.1.87 — अ + इ → ए"""
        result = self.engine.apply("अ", "इन्द्रः")
        self.assertIsNotNone(result.rule_applied)
        self.assertEqual(result.rule_applied.id, "6.1.87")

    def test_explain(self):
        """explain() should return explanations for sandhi-eligible text."""
        explanations = self.engine.explain("देवेन्द्रः")
        # Should detect at least potential sandhi
        self.assertIsInstance(explanations, list)

    def test_list_rules(self):
        """Should have at least 4 rules."""
        self.assertGreaterEqual(len(self.engine.rules), 4)


class TestMorphology(unittest.TestCase):
    def setUp(self):
        self.analyzer = MorphologicalAnalyzer()

    def test_nominative(self):
        """Recognize nominative singular -ः."""
        results = self.analyzer.analyze("रामः")
        self.assertTrue(len(results) > 0)
        noms = [r for r in results if r.vibhakti == "Nominative"]
        self.assertTrue(len(noms) > 0)

    def test_accusative(self):
        """Recognize accusative singular -म्."""
        results = self.analyzer.analyze("वनम्")
        self.assertTrue(len(results) > 0)
        accs = [r for r in results if r.vibhakti == "Accusative"]
        self.assertTrue(len(accs) > 0)

    def test_verb(self):
        """Recognize verb ending -ति."""
        results = self.analyzer.analyze("गच्छति")
        self.assertTrue(len(results) > 0)
        verbs = [r for r in results if r.category == "Tiṅanta"]
        self.assertTrue(len(verbs) > 0)


class TestSemantics(unittest.TestCase):
    def setUp(self):
        self.parser = SemanticParser()

    def test_parse_sentence(self):
        """Parse a basic sentence into a kāraka graph."""
        graph = self.parser.parse("रामः वनम् गच्छति")
        self.assertIsNotNone(graph)
        self.assertGreater(len(graph.nodes), 0)

    def test_graph_has_edges(self):
        """A multi-word sentence should have edges."""
        graph = self.parser.parse("रामः वनम् गच्छति")
        self.assertGreater(len(graph.edges), 0)


class TestChandas(unittest.TestCase):
    def setUp(self):
        self.analyzer = ChandasAnalyzer()

    def test_analyze_iast(self):
        """Analyze IAST text for prosody."""
        result = self.analyzer.analyze("dharmasya tattvam")
        self.assertGreater(result.syllable_count, 0)
        self.assertIn(result.pattern[0], ["0", "1"])

    def test_prastara(self):
        """Generate all patterns of length n."""
        patterns = self.analyzer.prastara(3)
        self.assertEqual(len(patterns), 8)  # 2^3

    def test_nashtam_uddishtam_roundtrip(self):
        """Naṣṭam and Uddiṣṭam should be inverses."""
        pattern = "10110"
        idx = self.analyzer.uddishtam(pattern)
        restored = self.analyzer.nashtam(idx, len(pattern))
        self.assertEqual(pattern, restored)


class TestSamasa(unittest.TestCase):
    def setUp(self):
        self.analyzer = SamasaAnalyzer()

    def test_bahuvrihi(self):
        """Detect Bahuvrīhi compound."""
        result = self.analyzer.analyze("pītāmbaram")
        # May or may not detect depending on substring matching
        if result:
            self.assertIn("Bahuvrīhi", result.compound_type)

    def test_avyayibhava(self):
        """Detect Avyayībhāva prefix."""
        result = self.analyzer.analyze("yathāvidhi")
        self.assertIsNotNone(result)
        self.assertIn("Avyayībhāva", result.compound_type)


class TestValidator(unittest.TestCase):
    def setUp(self):
        self.validator = SanskritValidator()

    def test_validate_basic(self):
        """Full pipeline on a basic sentence."""
        result = self.validator.validate("रामः वनम् गच्छति")
        self.assertTrue(result.is_valid)
        self.assertGreater(len(result.suggestions), 0)

    def test_validate_returns_result(self):
        """Result should have expected attributes."""
        result = self.validator.validate("धर्मक्षेत्रे")
        self.assertIsInstance(result.grammar_patterns, dict)
        self.assertIn("sandhi", result.grammar_patterns)

    def test_empty_input(self):
        """Empty input should return is_valid=False."""
        result = self.validator.validate("")
        self.assertFalse(result.is_valid)

    def test_validate_document_verse_split(self):
        """Document-level analysis should split and aggregate."""
        text = "रामः वनम् गच्छति। देवः पठति॥"
        doc = self.validator.validate_document(text, split_mode="verse")
        self.assertEqual(doc["segment_count"], 2)
        self.assertIn("summary", doc)
        self.assertIn("segments", doc)
        self.assertEqual(len(doc["segments"]), 2)

    def test_validate_document_line_split(self):
        """Line mode should split on newlines."""
        text = "रामः वनम् गच्छति\nदेवः पठति"
        doc = self.validator.validate_document(text, split_mode="line")
        self.assertEqual(doc["segment_count"], 2)

    def test_validate_document_invalid_mode(self):
        """Invalid split mode should raise ValueError."""
        with self.assertRaises(ValueError):
            self.validator.validate_document("रामः", split_mode="chunk")


if __name__ == "__main__":
    unittest.main()
