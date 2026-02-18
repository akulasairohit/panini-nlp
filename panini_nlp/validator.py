"""
Sanskrit Validator — full NLP pipeline.

Orchestrates sandhi, morphology, semantics, samāsa, and chandas
analysis into a single ``validate()`` call that returns a structured
``ValidationResult``.
"""

from dataclasses import dataclass, field
from enum import Enum
import re
from typing import Any, Dict, List, Optional

from panini_nlp.sandhi import SandhiEngine
from panini_nlp.morphology import MorphologicalAnalyzer
from panini_nlp.semantics import SemanticParser
from panini_nlp.samasa import SamasaAnalyzer
from panini_nlp.chandas import ChandasAnalyzer

__all__ = ["SanskritValidator", "ValidationResult", "Severity"]


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ValidationResult:
    """Full analysis result from ``SanskritValidator.validate()``."""

    text: str
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    confidence: float = 1.0
    grammar_patterns: Dict[str, int] = field(default_factory=dict)
    semantic_graph: Optional[Dict[str, Any]] = None
    meter: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
            "confidence": self.confidence,
            "grammar_patterns": self.grammar_patterns,
            "semantic_graph": self.semantic_graph,
            "meter": self.meter,
        }


class SanskritValidator:
    """
    Full Sanskrit NLP pipeline.

    Combines all panini-nlp modules to analyze a Sanskrit sentence:

    1. Sandhi detection (potential junction points)
    2. Morphological analysis of each word
    3. Kāraka-based semantic graph construction
    4. Compound (samāsa) identification
    5. Meter (chandas) analysis

    Example
    -------
    >>> v = SanskritValidator()
    >>> r = v.validate("रामः वनम् गच्छति")
    >>> r.is_valid
    True
    >>> len(r.suggestions) > 0
    True
    """

    def __init__(self) -> None:
        self.sandhi = SandhiEngine()
        self.morphology = MorphologicalAnalyzer()
        self.semantics = SemanticParser()
        self.samasa = SamasaAnalyzer()
        self.chandas = ChandasAnalyzer()

    def validate(self, text: str) -> ValidationResult:
        """Run the full analysis pipeline on *text*."""
        result = ValidationResult(text=text)
        words = text.strip().split()

        if not words:
            result.is_valid = False
            result.errors.append("Empty input.")
            return result

        patterns = {"sandhi": 0, "samasa": 0, "vibhakti": 0, "dhatu": 0}

        # ── 1. Sandhi analysis ───────────────────────────────────────────
        self._analyze_sandhi(text, result, patterns)

        # ── 2. Morphological analysis ────────────────────────────────────
        self._analyze_morphology(words, result, patterns)

        # ── 3. Semantic graph ────────────────────────────────────────────
        self._analyze_semantics(text, result)

        # ── 4. Compound analysis ─────────────────────────────────────────
        self._analyze_compounds(words, result, patterns)

        # ── 5. Meter analysis ────────────────────────────────────────────
        self._analyze_meter(text, result)

        result.grammar_patterns = patterns
        return result

    def validate_document(
        self,
        text: str,
        split_mode: str = "verse",
        include_empty: bool = False,
    ) -> Dict[str, Any]:
        """
        Analyze a larger Sanskrit document by splitting it into manageable segments.

        Parameters
        ----------
        text:
            Full input text (multi-line or multi-verse).
        split_mode:
            "verse" (default), "line", or "sentence".
        include_empty:
            Whether to keep empty segments after splitting.

        Returns
        -------
        dict with:
            - split_mode
            - segment_count
            - summary (aggregated pattern counts and validity)
            - segments (per-segment ValidationResult as dict)
        """
        segments = self._split_document(text, split_mode=split_mode)
        if not include_empty:
            segments = [
                s for s in segments
                if s.strip() and not self._is_noise_segment(s)
            ]

        results: List[Dict[str, Any]] = []
        totals = {"sandhi": 0, "samasa": 0, "vibhakti": 0, "dhatu": 0}
        valid_count = 0

        for index, segment in enumerate(segments, start=1):
            vr = self.validate(segment)
            if vr.is_valid:
                valid_count += 1

            for key in totals:
                totals[key] += vr.grammar_patterns.get(key, 0)

            results.append(
                {
                    "index": index,
                    "text": segment,
                    "result": vr.to_dict(),
                }
            )

        segment_count = len(results)
        invalid_count = segment_count - valid_count

        return {
            "split_mode": split_mode,
            "segment_count": segment_count,
            "summary": {
                "valid_segments": valid_count,
                "invalid_segments": invalid_count,
                "totals": totals,
            },
            "segments": results,
        }

    @staticmethod
    def _split_document(text: str, split_mode: str = "verse") -> List[str]:
        mode = split_mode.strip().lower()
        if mode == "line":
            return [line.strip() for line in text.splitlines()]
        if mode == "sentence":
            return [s.strip() for s in re.split(r"[।॥.!?\n]+", text)]
        if mode == "verse":
            return [s.strip() for s in re.split(r"[।॥\n]+", text)]
        raise ValueError("split_mode must be one of: verse, line, sentence")

    @staticmethod
    def _is_noise_segment(segment: str) -> bool:
        """Return True for numbering/punctuation-only fragments."""
        return bool(re.fullmatch(r"[\s\(\)\[\]{}०-९0-9\.,:;\-_/]+", segment))

    # ── private helpers ──────────────────────────────────────────────────

    def _analyze_sandhi(
        self, text: str, result: ValidationResult, patterns: Dict[str, int]
    ) -> None:
        explanations = self.sandhi.explain(text)
        if explanations:
            for exp in explanations:
                result.suggestions.append(exp)
                patterns["sandhi"] += 1

    def _analyze_morphology(
        self,
        words: List[str],
        result: ValidationResult,
        patterns: Dict[str, int],
    ) -> None:
        for word in words:
            analyses = self.morphology.analyze(word)
            if analyses:
                for a in analyses:
                    parts = f"{a.stem} + {a.suffix}"
                    role = self.morphology.get_karaka(a)
                    role_str = f" -> Role: {role}" if role and role != "Unknown" else ""
                    if a.vibhakti:
                        label = f"[{a.vibhakti} {a.vacana}]"
                    elif a.lakara:
                        label = f"[{a.lakara} {a.purusha} {a.vacana}]"
                    else:
                        label = "[unanalyzed]"
                    result.suggestions.append(
                        f"Morphology ({word}): {parts} {label}{role_str}"
                    )
                    if a.vibhakti:
                        patterns["vibhakti"] += 1
                    if a.lakara:
                        patterns["dhatu"] += 1

    def _analyze_semantics(
        self, text: str, result: ValidationResult
    ) -> None:
        graph = self.semantics.parse(text)
        if graph and graph.nodes:
            result.suggestions.append("--- Semantic Network (Kāraka) ---")
            for edge in graph.edges:
                src = next(
                    (n for n in graph.nodes if n.id == edge.source_id), None
                )
                tgt = next(
                    (n for n in graph.nodes if n.id == edge.target_id), None
                )
                if src and tgt:
                    result.suggestions.append(
                        f"{src.label} --[{edge.relation}]--> {tgt.label}"
                    )
            result.semantic_graph = {
                "nodes": [
                    {"id": n.id, "label": n.label, "type": n.type,
                     "metadata": n.metadata}
                    for n in graph.nodes
                ],
                "edges": [
                    {"source": e.source_id, "target": e.target_id,
                     "relation": e.relation}
                    for e in graph.edges
                ],
            }

    def _analyze_compounds(
        self,
        words: List[str],
        result: ValidationResult,
        patterns: Dict[str, int],
    ) -> None:
        for word in words:
            sa = self.samasa.analyze(word)
            if sa:
                result.suggestions.append(
                    f"Compound ({word}): {sa.compound_type} — "
                    f"{' + '.join(sa.constituents)} → {sa.meaning_structure}"
                )
                patterns["samasa"] += 1

    def _analyze_meter(self, text: str, result: ValidationResult) -> None:
        meter_result = self.chandas.analyze(text)
        if meter_result.syllable_count > 0:
            result.meter = meter_result.meter_name
            result.suggestions.append(
                f"Meter: {meter_result.meter_name} "
                f"(pattern={meter_result.pattern}, "
                f"syllables={meter_result.syllable_count})"
            )
