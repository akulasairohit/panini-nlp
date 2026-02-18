#!/usr/bin/env python3
"""Example: line-by-line meaning analysis."""

from panini_nlp import SanskritMeaningEngine


def main() -> None:
    text = """रामः वनम् गच्छति।
देवः पठति॥"""

    engine = SanskritMeaningEngine()
    report = engine.analyze_document_meaning(text, split_mode="verse", meaning_mode="fluent")

    print("=" * 72)
    print("Panini NLP — Meaning Analysis")
    print("=" * 72)
    print(f"segments: {report.segment_count}")
    print(f"summary: {report.summary}")
    print()

    for seg in report.segments:
        print(f"[{seg.index}] {seg.source}")
        print(f"  meaning: {seg.meaning}")
        print(f"  confidence: {seg.confidence}")


if __name__ == "__main__":
    main()
