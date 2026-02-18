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
from .sounds import (
    Phoneme, A, AA, I, II, U, UU, R, RR, L, E, AI, O, AU,
    YA, VA, RA, LA, AC
)
from .text.processing import decompose, recompose

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
    v0.2: Uses Phoneme processing (Varna-Vibhasha).

    >>> engine = SandhiEngine()
    >>> engine.apply("देव", "आलय").modified
    'देवालय'
    """

    def __init__(self) -> None:
        self.rules = list(_RULES)
        
        # Precompute sets for pratyaharas
        self.AK = {A.symbol, AA.symbol, I.symbol, II.symbol, U.symbol, UU.symbol, R.symbol, RR.symbol, L.symbol}
        self.IK = {I.symbol, II.symbol, U.symbol, UU.symbol, R.symbol, RR.symbol, L.symbol}
        self.AC = AC # From sounds.py
        
        # Mapping for Yan Sandhi replacement (Ik -> Yan)
        # i/I -> y, u/U -> v, r/R -> r, l -> l
        self.YAN_MAP = {
            I.symbol: YA, II.symbol: YA,
            U.symbol: VA, UU.symbol: VA,
            R.symbol: RA, RR.symbol: RA,
            L.symbol: LA
        }

    # ── public API ───────────────────────────────────────────────────────────

    def apply(self, term1: str, term2: str) -> SandhiResult:
        """Combine two terms applying the highest-priority Sandhi."""
        t1 = term1.strip()
        t2 = term2.strip()
        if not t1 or not t2:
            return SandhiResult(f"{t1} + {t2}", f"{t1}{t2}", None, 1.0)
            
        # 1. Decompose into Phonemes
        p1 = decompose(t1)
        p2 = decompose(t2)
        
        if not p1 or not p2:
            return SandhiResult(f"{t1} + {t2}", f"{t1}{t2}", None, 1.0)

        last = p1[-1]
        first = p2[0]
        
        # Logic is easier to read with symbols
        L_sym = last.symbol
        F_sym = first.symbol
        
        # Check Rules in Priority Order (simplified for now)

        # 6.1.101 — Savarṇa Dīrgha (Akah Savarne Dirghah)
        # Condition: Ak + Savarna (Similar Vowel) -> Dirgha
        # Savarna: Same place of articulation.
        if last.is_vowel and first.is_vowel:
            if last.place == first.place and L_sym in self.AK:
                # Merge into Long Vowel
                replacement = None
                if L_sym in {A.symbol, AA.symbol}: replacement = AA
                elif L_sym in {I.symbol, II.symbol}: replacement = II
                elif L_sym in {U.symbol, UU.symbol}: replacement = UU
                elif L_sym in {R.symbol, RR.symbol}: replacement = RR
                # L usually doesn't have long form in classic, but theoretical
                
                if replacement:
                    new_phonemes = p1[:-1] + [replacement] + p2[1:]
                    return self._result(t1, t2, new_phonemes, "6.1.101")

        # 6.1.88 — Vṛddhi (Vrddhir Eci)
        # Condition: A/AA + Ec (e, o, ai, au) -> Vrddhi (ai, au)
        # Note: Standard sutra says "Eci" (e, o, ai, au).
        if L_sym in {A.symbol, AA.symbol} and first.is_vowel:
             replacement = None
             if F_sym in {E.symbol, AI.symbol}: replacement = AI
             elif F_sym in {O.symbol, AU.symbol}: replacement = AU
             
             if replacement:
                 new_phonemes = p1[:-1] + [replacement] + p2[1:]
                 return self._result(t1, t2, new_phonemes, "6.1.88")

        # 6.1.87 — Guṇa (Ad Gunah)
        # Condition: A/AA + Ac (simple vowels mostly, but exceptions covered by Vrddhi)
        # A + I -> E, A + U -> O, A + R -> Ar, A + L -> Al
        if L_sym in {A.symbol, AA.symbol} and first.is_vowel:
             replacement = []
             if F_sym in {I.symbol, II.symbol}: replacement = [E]
             elif F_sym in {U.symbol, UU.symbol}: replacement = [O]
             elif F_sym in {R.symbol, RR.symbol}: replacement = [A, RA] # Ar
             elif F_sym in {L.symbol}: replacement = [A, LA] # Al
             
             if replacement:
                 new_phonemes = p1[:-1] + replacement + p2[1:]
                 return self._result(t1, t2, new_phonemes, "6.1.87")

        # 6.1.77 — Yaṇ (Iko Yanaci)
        # Condition: Ik + Ac (dissimilar) -> Yan
        if L_sym in self.IK and first.is_vowel:
            # Check dissimilarity (simplified: not same place)
            # Actually Savarna Dirgha (6.1.101) is an exception to Yan.
            # Since we checked 6.1.101 first, we are safe to apply Yan if 101 didn't match.
            # (In Panini, Paratvat (later rule) applies, but 6.1.101 is later than 6.1.77 so it wins anyway).
            
            if L_sym in self.YAN_MAP:
                yan = self.YAN_MAP[L_sym]
                new_phonemes = p1[:-1] + [yan] + p2 # Keep the following vowel!
                return self._result(t1, t2, new_phonemes, "6.1.77")

        # No applicable rule
        return SandhiResult(f"{t1} + {t2}", f"{t1} {t2}", None, 0.0)

    def explain(self, text: str) -> List[str]:
        """Heuristic reverse-engineering."""
        # TODO: Upgrade to phoneme based explanation
        explanations: List[str] = []
        if "्य" in text or "्व" in text:
             explanations.append("Possible Yaṇ Sandhi (6.1.77)")
        if "े" in text or "ो" in text:
             explanations.append("Possible Guṇa Sandhi (6.1.87)")
        if "ै" in text or "ौ" in text:
             explanations.append("Possible Vṛddhi Sandhi (6.1.88)")
        if "ा" in text or "ी" in text or "ू" in text:
             explanations.append("Possible Savarṇa Dīrgha (6.1.101)")
        return explanations

    def list_rules(self) -> List[Sutra]:
        """Return all loaded Sandhi rules."""
        return list(self.rules)

    # ── helpers ──────────────────────────────────────────────────────────────

    def _result(self, t1: str, t2: str, phonemes: List[Phoneme], rid: str) -> SandhiResult:
        combined = recompose(phonemes)
        return SandhiResult(
            original=f"{t1} + {t2}",
            modified=combined,
            rule_applied=_rule(rid),
            confidence=1.0,
        )
