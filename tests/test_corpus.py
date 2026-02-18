"""Tests for full corpus loaders (Aṣṭādhyāyī + Dhātupāṭha)."""

import unittest

from panini_nlp.corpus import AshtadhyayiCorpus, DhatupathaCorpus, SanskritCorpus


class TestAshtadhyayiCorpus(unittest.TestCase):
    def setUp(self):
        self.corpus = AshtadhyayiCorpus()

    def test_count_is_large(self):
        self.assertGreater(self.corpus.count, 3900)

    def test_get_by_ascii_id(self):
        s = self.corpus.get("1.1.1")
        self.assertIsNotNone(s)
        self.assertIn("वृद्धि", s.text)

    def test_search(self):
        hits = self.corpus.search("गुण")
        self.assertGreater(len(hits), 0)


class TestDhatupathaCorpus(unittest.TestCase):
    def setUp(self):
        self.corpus = DhatupathaCorpus()

    def test_count_is_large(self):
        self.assertGreater(self.corpus.count, 2200)

    def test_get_known_dhatu(self):
        d = self.corpus.get("1.1")
        self.assertIsNotNone(d)
        self.assertIn("भू", d.dhatu)

    def test_find_roots(self):
        hits = self.corpus.find_roots("भू")
        self.assertGreater(len(hits), 0)


class TestSanskritCorpus(unittest.TestCase):
    def test_wrapper(self):
        c = SanskritCorpus()
        self.assertGreater(c.ashtadhyayi.count, 3900)
        self.assertGreater(c.dhatupatha.count, 2200)


if __name__ == "__main__":
    unittest.main()
