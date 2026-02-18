"""
Piṅgala Chandas (Prosody / Meter) Analyzer.

Implements the algorithms from Piṅgala's Chandaḥśāstra (c. 200 BCE):
  - Laghu/Guru quantization of Sanskrit text
  - Prastāra enumeration (all 2^n meter patterns)
  - Naṣṭam (index → pattern)
  - Uddiṣṭam (pattern → index)
  - Meter identification (Gāyatrī, Anuṣṭubh, Triṣṭubh, Jagatī, …)

Works on both IAST (Roman) and Devanāgarī input.
"""

from typing import Dict, List, Optional, Tuple

__all__ = ["ChandasAnalyzer", "MeterResult"]


class MeterResult:
    """Result of a meter analysis."""

    def __init__(self, text: str, pattern: str) -> None:
        self.text = text
        self.pattern = pattern      # "0110…" (0=laghu, 1=guru)
        self.syllable_count = len(pattern)
        self.laghu_count = pattern.count("0")
        self.guru_count = pattern.count("1")
        self.decimal = int(pattern, 2) if pattern else 0
        self.meter_name = self._identify_meter()

    def _identify_meter(self) -> str:
        n = self.syllable_count
        if n == 0:
            return "Unknown"
        # pada-level identification (quarter-verse)
        if n == 6:
            return "Gāyatrī (6)"
        if n == 7:
            return "Uṣṇih (7)"
        if 7 <= n <= 8:
            return "Anuṣṭubh / Śloka (8)"
        if n == 9:
            return "Bṛhatī (9)"
        if n == 11:
            return "Triṣṭubh (11)"
        if n == 12:
            return "Jagatī (12)"
        return f"Unclassified ({n} syllables)"

    def __repr__(self) -> str:
        ratio = (
            f"{self.laghu_count}:{self.guru_count}"
            if self.guru_count
            else f"{self.laghu_count}:0"
        )
        return (
            f"MeterResult(meter={self.meter_name!r}, pattern={self.pattern!r}, "
            f"syllables={self.syllable_count}, L:G={ratio})"
        )


class ChandasAnalyzer:
    """
    Piṅgala-based prosodic analyzer for Sanskrit.

    >>> ch = ChandasAnalyzer()
    >>> r = ch.analyze("Dharmasya tattvam nihitam guhayam")
    >>> r.pattern
    '10110011'
    """

    # ── IAST vowel classification ────────────────────────────────────────────
    _SHORT_VOWELS_IAST = frozenset("aiuṛḷ")
    _LONG_VOWELS_IAST = frozenset(
        ["ā", "ī", "ū", "ṝ", "ḹ", "e", "ai", "o", "au",
         "A", "I", "U", "E", "O"]
    )
    _ANUSVARA_VISARGA = frozenset(["ṃ", "ḥ", "M", "H"])

    # ── Devanāgarī classification ───────────────────────────────────────────
    _SHORT_V_DEV = frozenset("अइउऋऌ")
    _LONG_V_DEV = frozenset("आईऊॠऌएऐओऔ")
    _SHORT_MATRA = frozenset("िुृ")
    _LONG_MATRA = frozenset("ाीूॄेैोौ")
    _ANUSVARA_DEV = frozenset("ंः")
    _VIRAMA = "्"
    _DEV_CONSONANTS = frozenset(
        "कखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह"
    )

    def __init__(self) -> None:
        pass

    # ── public API ───────────────────────────────────────────────────────────

    def analyze(self, text: str) -> MeterResult:
        """Analyze prosody of Sanskrit text → MeterResult."""
        # Detect script
        if any(c in self._DEV_CONSONANTS or c in self._SHORT_V_DEV or c in self._LONG_V_DEV for c in text):
            pattern = self._quantize_devanagari(text)
        else:
            pattern = self._quantize_iast(text)
        return MeterResult(text, pattern)

    def prastara(self, n: int) -> List[str]:
        """Generate all 2^n binary meter patterns of length *n*."""
        return [bin(i)[2:].zfill(n) for i in range(2 ** n)]

    def nashtam(self, index: int, length: int) -> str:
        """Naṣṭam: given an index, return the meter pattern (index → pattern)."""
        return bin(index)[2:].zfill(length)

    def uddishtam(self, pattern: str) -> int:
        """Uddiṣṭam: given a pattern, return its index (pattern → index)."""
        return int(pattern, 2)

    # ── Devanāgarī quantizer ─────────────────────────────────────────────────

    def _quantize_devanagari(self, text: str) -> str:
        clean = text.replace(" ", "").replace("।", "").replace("॥", "").replace("\n", "")
        chars = list(clean)
        bits: List[str] = []
        i = 0
        n = len(chars)

        while i < n:
            ch = chars[i]

            # Independent vowel
            if ch in self._SHORT_V_DEV or ch in self._LONG_V_DEV:
                weight = "1" if ch in self._LONG_V_DEV else "0"
                # Check for anusvāra / visarga after
                if i + 1 < n and chars[i + 1] in self._ANUSVARA_DEV:
                    weight = "1"
                    i += 1
                # Saṃyoga: short + 2+ consonants → guru
                if weight == "0":
                    weight = self._check_samyoga(chars, i, n)
                bits.append(weight)
                i += 1
                continue

            # Consonant + mātrā
            if ch in self._DEV_CONSONANTS:
                # Skip consonant clusters (virāma-joined)
                while i + 1 < n and chars[i + 1] == self._VIRAMA:
                    i += 2  # skip virāma + next consonant
                    if i >= n:
                        break
                i += 1
                if i >= n:
                    break
                nxt = chars[i]
                if nxt in self._SHORT_MATRA:
                    weight = "0"
                    if i + 1 < n and chars[i + 1] in self._ANUSVARA_DEV:
                        weight = "1"
                        i += 1
                    if weight == "0":
                        weight = self._check_samyoga(chars, i, n)
                    bits.append(weight)
                    i += 1
                elif nxt in self._LONG_MATRA:
                    bits.append("1")
                    i += 1
                elif nxt in self._ANUSVARA_DEV:
                    bits.append("1")
                    i += 1
                elif nxt == self._VIRAMA:
                    # Consonant with halant — no vowel — skip
                    i += 1
                else:
                    # Inherent 'a' (short)
                    weight = self._check_samyoga(chars, i - 1, n)
                    bits.append(weight)
                continue

            # mātrā without preceding consonant (shouldn't happen normally)
            if ch in self._SHORT_MATRA:
                bits.append("0")
                i += 1
            elif ch in self._LONG_MATRA:
                bits.append("1")
                i += 1
            else:
                i += 1  # skip unknown

        return "".join(bits)

    def _check_samyoga(self, chars: list, pos: int, n: int) -> str:
        """Check if a short vowel at *pos* is made guru by following conjunct."""
        consonants = 0
        j = pos + 1
        while j < n:
            c = chars[j]
            if c == self._VIRAMA:
                j += 1
                continue
            if c in self._DEV_CONSONANTS:
                consonants += 1
                j += 1
            else:
                break
        return "1" if consonants >= 2 else "0"

    # ── IAST quantizer ───────────────────────────────────────────────────────

    def _quantize_iast(self, text: str) -> str:
        clean = text.replace(" ", "").replace("|", "").replace("\n", "")
        bits: List[str] = []
        i = 0
        n = len(clean)

        while i < n:
            ch = clean[i]
            is_short = ch in self._SHORT_VOWELS_IAST
            is_long = ch in self._LONG_VOWELS_IAST

            if is_short or is_long:
                weight = "1" if is_long else "0"

                # Anusvāra / visarga → guru
                if i + 1 < n and clean[i + 1] in self._ANUSVARA_VISARGA:
                    weight = "1"

                # Saṃyoga: short vowel + 2+ consonants → guru
                if weight == "0":
                    cons = 0
                    j = i + 1
                    while j < n:
                        if clean[j] in self._ANUSVARA_VISARGA:
                            weight = "1"
                            break
                        if clean[j] not in self._SHORT_VOWELS_IAST and clean[j] not in self._LONG_VOWELS_IAST:
                            cons += 1
                            j += 1
                        else:
                            break
                    if cons > 1:
                        weight = "1"

                bits.append(weight)

            i += 1

        return "".join(bits)
