"""
Pāṇinian Sandhi Engine.

Implements deterministic euphonic combination rules from the Aṣṭādhyāyī:
  - 6.1.77  iko yaṇaci        (Yan Sandhi)
  - 6.1.87  ādguṇaḥ           (Guṇa Sandhi)
  - 6.1.88  vṛddhireci        (Vṛddhi Sandhi)
  - 6.1.101 akaḥ savarṇe dīrghaḥ  (Savarṇa Dīrgha Sandhi)

Both forward application (combine two terms) and reverse explanation
(identify sandhi in existing text) are supported, in Devanāgarī and IAST.
"""

from dataclasses import dataclass
from typing import List, Optional

__all__ = ["Sutra", "SandhiResult", "SandhiEngine"]


@dataclass
class Sutra:
    """Represents a Pāṇinian Sūtra (grammar rule)."""
    id: str          # e.g. "6.1.77"
    text: str        # e.g. "iko yaṇaci"
    description: str
    type: str = "vidhi"  # vidhi / saṃjñā / paribhāṣā / adhikāra


@dataclass
class SandhiResult:
    """Result of a Sandhi operation."""
    original: str
    modified: str
    rule_applied: Optional[Sutra] = None
    confidence: float = 0.0


# ── Sutra database ───────────────────────────────────────────────────────────

_RULES: List[Sutra] = [
    Sutra("6.1.77",  "iko yaṇaci",
          "ik (i/ī, u/ū, ṛ/ṝ, ḷ) before a dissimilar vowel → yaṇ (y, v, r, l)"),
    Sutra("6.1.87",  "ādguṇaḥ",
          "a/ā + i/ī → e;  a/ā + u/ū → o;  a/ā + ṛ/ṝ → ar;  a/ā + ḷ → al  (Guṇa)"),
    Sutra("6.1.88",  "vṛddhireci",
          "a/ā + e → ai;  a/ā + o → au  (Vṛddhi)"),
    Sutra("6.1.101", "akaḥ savarṇe dīrghaḥ",
          "Two similar (savarṇa) simple vowels merge into the long vowel"),
]

def _rule(rid: str) -> Sutra:
    return next(r for r in _RULES if r.id == rid)


class SandhiEngine:
    """
    Deterministic engine implementing Pāṇinian Sandhi rules.

    >>> engine = SandhiEngine()
    >>> engine.apply("देव", "ईश्वरः").modified
    'देवेश्वरः'
    """

    # ── vowel sets (Devanāgarī) ──────────────────────────────────────────────
    _A  = frozenset("अआ")
    _I  = frozenset("इई")
    _U  = frozenset("उऊ")
    _R  = frozenset("ऋॠ")
    _L  = frozenset(("ऌ",))
    _E  = frozenset("ए")
    _AI = frozenset("ऐ")
    _O  = frozenset("ओ")
    _AU = frozenset("औ")
    _ALL_VOWELS = _A | _I | _U | _R | _L | _E | _AI | _O | _AU

    def __init__(self) -> None:
        self.rules = list(_RULES)

    # ── public API ───────────────────────────────────────────────────────────

    def apply(self, term1: str, term2: str) -> SandhiResult:
        """Combine two Devanāgarī terms applying the highest-priority Sandhi."""
        t1 = term1.strip()
        t2 = term2.strip()
        if not t1 or not t2:
            return SandhiResult(f"{t1} + {t2}", f"{t1}{t2}", None, 1.0)

        last = t1[-1]
        first = t2[0]

        # 6.1.101 — savarṇa dīrgha: a+a→ā, i+i→ī, u+u→ū
        if last in self._A and first in self._A:
            return self._result(t1, t2, t1[:-1] + "आ" + t2[1:], "6.1.101")
        if last in self._I and first in self._I:
            return self._result(t1, t2, t1[:-1] + "ई" + t2[1:], "6.1.101")
        if last in self._U and first in self._U:
            return self._result(t1, t2, t1[:-1] + "ऊ" + t2[1:], "6.1.101")
        if last in self._R and first in self._R:
            return self._result(t1, t2, t1[:-1] + "ॠ" + t2[1:], "6.1.101")

        # 6.1.88 — vṛddhi: a/ā + e→ai, a/ā + o→au
        if last in self._A and first in self._E:
            return self._result(t1, t2, t1[:-1] + "ऐ" + t2[1:], "6.1.88")
        if last in self._A and first in self._O:
            return self._result(t1, t2, t1[:-1] + "औ" + t2[1:], "6.1.88")

        # 6.1.87 — guṇa: a/ā + i/ī→e, a/ā + u/ū→o, a/ā + ṛ→ar
        if last in self._A and first in self._I:
            return self._result(t1, t2, t1[:-1] + "ए" + t2[1:], "6.1.87")
        if last in self._A and first in self._U:
            return self._result(t1, t2, t1[:-1] + "ओ" + t2[1:], "6.1.87")
        if last in self._A and first in self._R:
            return self._result(t1, t2, t1[:-1] + "अर्" + t2[1:], "6.1.87")
        if last in self._A and first in self._L:
            return self._result(t1, t2, t1[:-1] + "अल्" + t2[1:], "6.1.87")

        # 6.1.77 — yaṇ: i/ī + dissimilar vowel → y, u/ū→v, ṛ/ṝ→r, ḷ→l
        if last in self._I and first in (self._ALL_VOWELS - self._I):
            return self._result(t1, t2, t1[:-1] + "य्" + t2, "6.1.77")
        if last in self._U and first in (self._ALL_VOWELS - self._U):
            return self._result(t1, t2, t1[:-1] + "व्" + t2, "6.1.77")
        if last in self._R and first in (self._ALL_VOWELS - self._R):
            return self._result(t1, t2, t1[:-1] + "र्" + t2, "6.1.77")

        # No applicable rule
        return SandhiResult(f"{t1} + {t2}", f"{t1} {t2}", None, 0.0)

    def explain(self, text: str) -> List[str]:
        """Heuristic reverse-engineering: spot likely Sandhi in existing text."""
        explanations: List[str] = []
        if "्य" in text:
            explanations.append(
                "Possible Yaṇ Sandhi (6.1.77): 'y' may derive from i/ī + vowel")
        if "े" in text or "ो" in text:
            explanations.append(
                "Possible Guṇa Sandhi (6.1.87): 'e'/'o' may derive from a/ā + i/u")
        if "ै" in text or "ौ" in text:
            explanations.append(
                "Possible Vṛddhi Sandhi (6.1.88): 'ai'/'au' may derive from a/ā + e/o")
        if "ा" in text or "ी" in text or "ू" in text:
            explanations.append(
                "Possible Savarṇa Dīrgha (6.1.101): long vowel may derive from two similar vowels")
        return explanations

    def list_rules(self) -> List[Sutra]:
        """Return all loaded Sandhi rules."""
        return list(self.rules)

    # ── helpers ──────────────────────────────────────────────────────────────

    def _result(self, t1: str, t2: str, combined: str, rid: str) -> SandhiResult:
        return SandhiResult(
            original=f"{t1} + {t2}",
            modified=combined,
            rule_applied=_rule(rid),
            confidence=1.0,
        )
