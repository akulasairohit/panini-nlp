"""
Samāsa (Compound) Analyzer for Sanskrit.

Identifies and decomposes Sanskrit compound words into their
constituent parts, classifying the compound type according to
Pāṇinian grammar:

  - Tatpuruṣa (Determinative)
  - Bahuvrīhi (Possessive / Exocentric)
  - Dvandva (Copulative)
  - Avyayībhāva (Adverbial)
  - Karmadhāraya (Descriptive / Appositional)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

__all__ = ["SamasaAnalyzer", "SamasaResult"]


@dataclass
class SamasaResult:
    """Result of compound analysis."""

    original: str
    constituents: List[str]
    compound_type: str
    meaning_structure: str


class SamasaAnalyzer:
    """
    Analyze Sanskrit compounds (samāsa).

    >>> sa = SamasaAnalyzer()
    >>> r = sa.analyze("pītāmbaram")
    >>> r.compound_type
    'Bahuvrīhi (Possessive)'
    """

    def __init__(self) -> None:
        # ── Avyayībhāva prefixes ─────────────────────────────────────────
        self.avyaya_prefixes = [
            "yathā", "yatha", "prati", "upa", "anu", "nir", "sah",
            "यथा", "प्रति", "उप", "अनु", "निर्", "सह",
        ]

        # ── Known lexical items  (IAST + Devanāgarī) ─────────────────────
        self.lexicon: Dict[str, str] = {
            # IAST
            "rāja": "king", "raja": "king",
            "puruṣa": "man", "purusha": "man",
            "nīla": "blue", "neela": "blue",
            "kamala": "lotus",
            "pīta": "yellow", "pita": "yellow",
            "ambara": "cloth",
            "rāma": "Rāma", "rama": "Rāma", "ram": "Rāma",
            "kṛṣṇa": "Kṛṣṇa", "krishna": "Kṛṣṇa",
            "gaja": "elephant",
            "ānana": "face", "anana": "face",
            "deva": "god",
            "dāsa": "servant", "dasa": "servant",
            "dharma": "dharma",
            "artha": "wealth",
            "kāma": "desire", "kama": "desire",
            "mokṣa": "liberation", "moksha": "liberation",
            "nara": "man",
            "siṃha": "lion", "simha": "lion",
            "mahā": "great", "maha": "great",
            # Devanāgarī
            "राज": "king",
            "पुरुष": "man",
            "नील": "blue",
            "कमल": "lotus",
            "पीत": "yellow",
            "अम्बर": "cloth",
            "राम": "Rāma",
            "कृष्ण": "Kṛṣṇa",
            "गज": "elephant",
            "आनन": "face",
            "देव": "god",
            "दास": "servant",
            "धर्म": "dharma",
            "अर्थ": "wealth",
            "काम": "desire",
            "मोक्ष": "liberation",
            "नर": "man",
            "सिंह": "lion",
            "महा": "great",
        }

    # ── public API ───────────────────────────────────────────────────────

    def analyze(self, word: str) -> Optional[SamasaResult]:
        """Analyze a potential compound word and return `SamasaResult`."""
        clean = word.strip()
        stem = self._strip_ending(clean.lower())

        # 1 — Avyayībhāva
        for prefix in self.avyaya_prefixes:
            if clean.lower().startswith(prefix):
                remainder = clean[len(prefix):]
                if remainder:
                    return SamasaResult(
                        original=word,
                        constituents=[prefix, remainder],
                        compound_type="Avyayībhāva (Adverbial)",
                        meaning_structure=f"In the manner of / regarding {remainder}",
                    )

        # 2 — Dvandva (dual ending -au / -ौ)
        result = self._try_dvandva(word, clean, stem)
        if result:
            return result

        # 3 — Bahuvrīhi (pattern-matched known compounds)
        result = self._try_bahuvrihi(word, stem)
        if result:
            return result

        # 4 — Karmadhāraya
        result = self._try_karmadharaya(word, stem)
        if result:
            return result

        # 5 — Tatpuruṣa (generic split)
        result = self._try_tatpurusha(word, stem)
        if result:
            return result

        return None

    # ── private helpers ──────────────────────────────────────────────────

    @staticmethod
    def _strip_ending(s: str) -> str:
        for suffix in ("ḥ", "h", "m", "ṁ", "म्", "ः"):
            if s.endswith(suffix):
                return s[: -len(suffix)]
        return s

    def _in_lex(self, part: str) -> bool:
        return part in self.lexicon or (part + "a") in self.lexicon

    def _try_dvandva(self, word: str, clean: str, stem: str) -> Optional[SamasaResult]:
        lc = clean.lower()
        if not (lc.endswith("au") or clean.endswith("ौ")):
            return None
        base = lc[:-2] if lc.endswith("au") else lc[:-1]
        for i in range(1, len(base)):
            p1, p2 = base[:i], base[i:]
            if self._in_lex(p1) and self._in_lex(p2):
                return SamasaResult(
                    original=word,
                    constituents=[p1, p2],
                    compound_type="Dvandva (Copulative)",
                    meaning_structure=f"{p1} and {p2}",
                )
        return None

    def _try_bahuvrihi(self, word: str, stem: str) -> Optional[SamasaResult]:
        patterns = [
            (["pīta", "pita", "पीत"], ["ambara", "अम्बर", "āmbara"],
             "One who has yellow garments (Viṣṇu)"),
            (["gaja", "गज"], ["ānana", "anana", "आनन"],
             "One who has an elephant face (Gaṇeśa)"),
            (["nara", "नर"], ["siṃha", "simha", "सिंह"],
             "One who is a lion among men (Viṣṇu)"),
        ]
        for firsts, seconds, meaning in patterns:
            for f in firsts:
                for s in seconds:
                    if f in stem and s in stem:
                        return SamasaResult(
                            original=word,
                            constituents=[f, s],
                            compound_type="Bahuvrīhi (Possessive)",
                            meaning_structure=meaning,
                        )
        return None

    def _try_karmadharaya(self, word: str, stem: str) -> Optional[SamasaResult]:
        patterns = [
            (["nīla", "neela", "नील"], ["kamala", "कमल"], "The blue lotus"),
            (["mahā", "maha", "महा"], ["deva", "देव"], "The great god"),
            (["mahā", "maha", "महा"], ["rāja", "raja", "राज"], "The great king"),
        ]
        for adjs, nouns, meaning in patterns:
            for a in adjs:
                for n in nouns:
                    if a in stem and n in stem:
                        return SamasaResult(
                            original=word,
                            constituents=[a, n],
                            compound_type="Karmadhāraya (Descriptive)",
                            meaning_structure=meaning,
                        )
        return None

    def _try_tatpurusha(self, word: str, stem: str) -> Optional[SamasaResult]:
        patterns = [
            (["rāja", "raja", "राज"], ["puruṣa", "purusha", "पुरुष"],
             "Man of the King"),
            (["deva", "देव"], ["dāsa", "dasa", "दास"],
             "Servant of god"),
            (["dharma", "धर्म"], ["artha", "अर्थ"],
             "Meaning of dharma"),
        ]
        for firsts, seconds, meaning in patterns:
            for f in firsts:
                for s in seconds:
                    if f in stem and s in stem:
                        return SamasaResult(
                            original=word,
                            constituents=[f, s],
                            compound_type="Tatpuruṣa (Determinative)",
                            meaning_structure=meaning,
                        )
        return None
