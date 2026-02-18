"""
Morphological Analyzer for Sanskrit.

Decomposes inflected Sanskrit words into:
  - Prakṛti  (stem / root)
  - Pratyaya (suffix)
  - Vibhakti (case)       — for Subanta (nominals)
  - Vacana   (number)
  - Liṅga    (gender)
  - Lakāra   (tense/mood) — for Tiṅanta (verbals)
  - Puruṣa   (person)

Currently covers:
  - a-stem masculine nouns  (rāma-śabda paradigm)
  - Present tense Parasmaipada & Ātmanepada verb endings
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

__all__ = ["MorphAnalysis", "MorphologicalAnalyzer"]


@dataclass
class MorphAnalysis:
    """Result of Pāṇinian morphological analysis."""
    original: str
    stem: str
    suffix: str
    category: str  # "Subanta" | "Tiṅanta" | "Avyaya"

    # Subanta features
    vibhakti: Optional[str] = None
    vacana: Optional[str] = None
    linga: Optional[str] = None

    # Tiṅanta features
    lakara: Optional[str] = None
    purusha: Optional[str] = None

    attributes: Dict[str, str] = field(default_factory=dict)
    meaning: Optional[str] = None


# ── Kāraka mapping ───────────────────────────────────────────────────────────

_KARAKA_MAP = {
    "Nominative":   "Kartā (Agent)",         # prathamā
    "Accusative":   "Karma (Object)",         # dvitīyā
    "Instrumental": "Karaṇa (Instrument)",    # tṛtīyā
    "Dative":       "Sampradāna (Recipient)", # caturthī
    "Ablative":     "Apādāna (Source)",       # pañcamī
    "Genitive":     "Sambandha (Relation)",   # ṣaṣṭhī
    "Locative":     "Adhikaraṇa (Location)",  # saptamī
    "Vocative":     "Sambodhana (Address)",   # sambodhana
}


class MorphologicalAnalyzer:
    """
    Rule-based morphological analyzer for Sanskrit.

    >>> analyzer = MorphologicalAnalyzer()
    >>> results = analyzer.analyze("रामस्य")
    >>> results[0].vibhakti
    'Genitive'
    """

    def __init__(self) -> None:
        # sup-pratyaya for a-stem masculine (rāma-śabda) — Devanāgarī + IAST
        self._noun_endings: Dict[str, Dict[str, str]] = {
            # Devanāgarī
            "ः":   {"case": "Nominative",   "number": "Singular"},
            "ौ":   {"case": "Nominative",   "number": "Dual"},
            "ाः":  {"case": "Nominative",   "number": "Plural"},
            "म्":  {"case": "Accusative",   "number": "Singular"},
            "ान्": {"case": "Accusative",   "number": "Plural"},
            "ेन":  {"case": "Instrumental", "number": "Singular"},
            "ेण":  {"case": "Instrumental", "number": "Singular"},
            "ाभ्याम्": {"case": "Instrumental", "number": "Dual"},
            "ैः":  {"case": "Instrumental", "number": "Plural"},
            "ाय":  {"case": "Dative",       "number": "Singular"},
            "ेभ्यः": {"case": "Dative",     "number": "Plural"},
            "ात्": {"case": "Ablative",     "number": "Singular"},
            "स्य": {"case": "Genitive",     "number": "Singular"},
            "योः": {"case": "Genitive",     "number": "Dual"},
            "ानाम्": {"case": "Genitive",   "number": "Plural"},
            "े":   {"case": "Locative",     "number": "Singular"},
            "ेषु": {"case": "Locative",     "number": "Plural"},
            # IAST
            "aḥ":   {"case": "Nominative",   "number": "Singular"},
            "au":   {"case": "Nominative",   "number": "Dual"},
            "āḥ":   {"case": "Nominative",   "number": "Plural"},
            "am":   {"case": "Accusative",   "number": "Singular"},
            "ān":   {"case": "Accusative",   "number": "Plural"},
            "ena":  {"case": "Instrumental", "number": "Singular"},
            "eṇa":  {"case": "Instrumental", "number": "Singular"},
            "ābhyām": {"case": "Instrumental", "number": "Dual"},
            "aiḥ":  {"case": "Instrumental", "number": "Plural"},
            "āya":  {"case": "Dative",       "number": "Singular"},
            "ebhyaḥ": {"case": "Dative",     "number": "Plural"},
            "āt":   {"case": "Ablative",     "number": "Singular"},
            "asya": {"case": "Genitive",     "number": "Singular"},
            "ayoḥ": {"case": "Genitive",     "number": "Dual"},
            "ānām": {"case": "Genitive",     "number": "Plural"},
            "e":    {"case": "Locative",     "number": "Singular"},
            "eṣu":  {"case": "Locative",     "number": "Plural"},
        }

        # tiṅ-pratyaya — Parasmaipada/Ātmanepada Laṭ (present)
        self._verb_endings: Dict[str, Dict[str, str]] = {
            # Devanāgarī
            "ति":   {"person": "Prathama", "number": "Singular"},
            "तः":   {"person": "Prathama", "number": "Dual"},
            "न्ति": {"person": "Prathama", "number": "Plural"},
            "सि":   {"person": "Madhyama", "number": "Singular"},
            "थः":   {"person": "Madhyama", "number": "Dual"},
            "थ":    {"person": "Madhyama", "number": "Plural"},
            "मि":   {"person": "Uttama",   "number": "Singular"},
            "वः":   {"person": "Uttama",   "number": "Dual"},
            "मः":   {"person": "Uttama",   "number": "Plural"},
            "ते":   {"person": "Prathama", "number": "Singular"},  # Ātmanepada
            # IAST
            "ti":   {"person": "Prathama", "number": "Singular"},
            "taḥ":  {"person": "Prathama", "number": "Dual"},
            "nti":  {"person": "Prathama", "number": "Plural"},
            "si":   {"person": "Madhyama", "number": "Singular"},
            "thaḥ": {"person": "Madhyama", "number": "Dual"},
            "tha":  {"person": "Madhyama", "number": "Plural"},
            "mi":   {"person": "Uttama",   "number": "Singular"},
            "vaḥ":  {"person": "Uttama",   "number": "Dual"},
            "maḥ":  {"person": "Uttama",   "number": "Plural"},
            "te":   {"person": "Prathama", "number": "Singular"},
        }

    # ── public API ───────────────────────────────────────────────────────────

    def analyze(self, word: str) -> List[MorphAnalysis]:
        """Return all possible morphological decompositions of *word*."""
        word = word.strip()
        analyses: List[MorphAnalysis] = []

        # Try longest-suffix-first for nouns
        for ending in sorted(self._noun_endings, key=len, reverse=True):
            if word.endswith(ending):
                attrs = self._noun_endings[ending]
                stem = word[: -len(ending)]
                analyses.append(MorphAnalysis(
                    original=word,
                    stem=stem,
                    suffix=ending,
                    category="Subanta",
                    vibhakti=attrs["case"],
                    vacana=attrs["number"],
                    linga="Masculine (a-stem)",
                    attributes=attrs,
                ))

        # Verbs
        for ending in sorted(self._verb_endings, key=len, reverse=True):
            if word.endswith(ending):
                attrs = self._verb_endings[ending]
                stem = word[: -len(ending)]
                analyses.append(MorphAnalysis(
                    original=word,
                    stem=stem,
                    suffix=ending,
                    category="Tiṅanta",
                    lakara="Laṭ (Present)",
                    purusha=attrs["person"],
                    vacana=attrs["number"],
                    attributes=attrs,
                ))

        # Fallback
        if not analyses:
            analyses.append(MorphAnalysis(
                original=word, stem=word, suffix="",
                category="Avyaya",
                attributes={"status": "unanalyzed"},
            ))

        return analyses

    @staticmethod
    def get_karaka(analysis: MorphAnalysis) -> str:
        """Map a Subanta vibhakti to its Kāraka (semantic role)."""
        if analysis.category == "Tiṅanta":
            return "Kriyā (Action)"
        return _KARAKA_MAP.get(analysis.vibhakti or "", "Unknown")
