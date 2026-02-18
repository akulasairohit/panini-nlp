"""Tests for meaning engine."""

import unittest

from panini_nlp.meaning import SanskritMeaningEngine


class TestMeaningEngine(unittest.TestCase):
    def test_fluent_fallback(self):
        engine = SanskritMeaningEngine()
        report = engine.analyze_document_meaning("रामः वनम् गच्छति।", split_mode="verse", meaning_mode="fluent")
        self.assertEqual(report.segment_count, 1)
        self.assertIn("Approximate meaning", report.segments[0].meaning)

    def test_literal_mode(self):
        engine = SanskritMeaningEngine()
        report = engine.analyze_document_meaning("रामः वनम् गच्छति।", split_mode="verse", meaning_mode="literal")
        self.assertEqual(report.segment_count, 1)
        self.assertIn("Literal gloss", report.segments[0].meaning)

    def test_custom_translator(self):
        engine = SanskritMeaningEngine(translator=lambda text: "Rama goes to the forest.")
        report = engine.analyze_document_meaning("रामः वनम् गच्छति।", split_mode="verse", meaning_mode="fluent")
        self.assertEqual(report.segments[0].meaning, "Rama goes to the forest.")
        self.assertGreaterEqual(report.summary["average_meaning_confidence"], 0.8)


if __name__ == "__main__":
    unittest.main()
