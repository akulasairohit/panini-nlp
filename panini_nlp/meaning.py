"""Line-by-line meaning engine for Sanskrit text.

This module adds a meaning layer on top of the grammar pipeline.
It supports:
- document splitting (verse/line/sentence)
- per-segment grammar analysis
- fluent translation via pluggable translator callback
- deterministic fallback gloss when no model translator is available
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from panini_nlp.morphology import MorphologicalAnalyzer
from panini_nlp.validator import SanskritValidator

__all__ = [
    "MeaningSegment",
    "MeaningReport",
    "SanskritMeaningEngine",
]


@dataclass
class MeaningSegment:
    index: int
    source: str
    meaning: str
    meaning_mode: str
    confidence: float
    grammar: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "source": self.source,
            "meaning": self.meaning,
            "meaning_mode": self.meaning_mode,
            "confidence": self.confidence,
            "grammar": self.grammar,
        }


@dataclass
class MeaningReport:
    split_mode: str
    segment_count: int
    summary: Dict[str, Any]
    segments: List[MeaningSegment]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "split_mode": self.split_mode,
            "segment_count": self.segment_count,
            "summary": self.summary,
            "segments": [s.to_dict() for s in self.segments],
        }


class SanskritMeaningEngine:
    """Generate line-by-line meaning with grammar context.

    Parameters
    ----------
    validator:
        Optional preconfigured ``SanskritValidator``.
    translator:
        Optional callable ``translator(text: str) -> str`` used for fluent output.
        If omitted, the engine falls back to deterministic heuristic meaning.
    """

    def __init__(
        self,
        validator: Optional[SanskritValidator] = None,
        translator: Optional[Callable[[str], str]] = None,
    ) -> None:
        self.validator = validator or SanskritValidator()
        self.morphology = MorphologicalAnalyzer()
        self.translator = translator

    def analyze_document_meaning(
        self,
        text: str,
        split_mode: str = "verse",
        meaning_mode: str = "fluent",
        require_fluent_model: bool = False,
    ) -> MeaningReport:
        """Analyze a full text and return line-by-line meaning."""
        doc = self.validator.validate_document(text, split_mode=split_mode)

        segments: List[MeaningSegment] = []
        for item in doc["segments"]:
            source = item["text"]
            grammar = item["result"]
            meaning, confidence, resolved_mode = self._render_meaning(
                source,
                meaning_mode=meaning_mode,
                require_fluent_model=require_fluent_model,
            )

            segments.append(
                MeaningSegment(
                    index=item["index"],
                    source=source,
                    meaning=meaning,
                    meaning_mode=resolved_mode,
                    confidence=confidence,
                    grammar=grammar,
                )
            )

        if segments:
            avg_conf = sum(s.confidence for s in segments) / len(segments)
        else:
            avg_conf = 0.0

        mode_counts: Dict[str, int] = {}
        for seg in segments:
            mode_counts[seg.meaning_mode] = mode_counts.get(seg.meaning_mode, 0) + 1

        summary = {
            "valid_segments": doc["summary"]["valid_segments"],
            "invalid_segments": doc["summary"]["invalid_segments"],
            "totals": doc["summary"]["totals"],
            "average_meaning_confidence": round(avg_conf, 3),
            "meaning_mode_requested": meaning_mode,
            "meaning_mode_breakdown": mode_counts,
        }

        return MeaningReport(
            split_mode=split_mode,
            segment_count=len(segments),
            summary=summary,
            segments=segments,
        )

    def _render_meaning(
        self,
        text: str,
        meaning_mode: str = "fluent",
        require_fluent_model: bool = False,
    ) -> tuple[str, float, str]:
        mode = meaning_mode.strip().lower()

        if mode == "fluent":
            if self.translator is not None:
                try:
                    translated = self.translator(text)
                    if translated and translated.strip():
                        return translated.strip(), 0.85, "fluent_model"
                except Exception:
                    pass
            if require_fluent_model:
                raise RuntimeError(
                    "Fluent model translation requested, but no translator callback is configured."
                )
            # fallback when no translator/model is available
            return self._heuristic_fluent(text), 0.45, "heuristic_fallback"

        if mode == "literal":
            return self._heuristic_literal(text), 0.55, "literal_heuristic"

        raise ValueError("meaning_mode must be one of: fluent, literal")

    def _heuristic_fluent(self, text: str) -> str:
        words = [w for w in text.split() if w.strip()]
        subjects: List[str] = []
        objects: List[str] = []
        verbs: List[str] = []

        for word in words:
            analyses = self.morphology.analyze(word)
            for analysis in analyses:
                if analysis.vibhakti == "Nominative":
                    subjects.append(analysis.stem or word)
                    break
                if analysis.vibhakti == "Accusative":
                    objects.append(analysis.stem or word)
                    break
                if analysis.category == "Tiṅanta":
                    verbs.append(analysis.stem or word)
                    break

        if subjects or objects or verbs:
            subj_txt = ", ".join(subjects) if subjects else "(implicit subject)"
            obj_txt = ", ".join(objects) if objects else "(no explicit object)"
            verb_txt = ", ".join(verbs) if verbs else "(action implied)"
            return (
                f"Approximate meaning: {subj_txt} performs {verb_txt} with respect to {obj_txt}."
            )

        return f"Approximate meaning (heuristic): {text}"

    def _heuristic_literal(self, text: str) -> str:
        words = [w for w in text.split() if w.strip()]
        parts: List[str] = []

        for word in words:
            analyses = self.morphology.analyze(word)
            first = analyses[0] if analyses else None
            if first and first.vibhakti:
                parts.append(f"{word}[{first.vibhakti}/{first.vacana}]")
            elif first and first.category == "Tiṅanta":
                parts.append(f"{word}[{first.lakara}/{first.purusha}/{first.vacana}]")
            else:
                parts.append(word)

        return "Literal gloss (heuristic): " + " ".join(parts)
