#!/usr/bin/env python3
"""Analyze a full Sanskrit text file with panini_nlp document mode."""

from pathlib import Path
import json
import sys

from panini_nlp import SanskritValidator


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 examples/analyze_document.py <input_file> [verse|line|sentence]")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    split_mode = sys.argv[2] if len(sys.argv) > 2 else "verse"

    if not input_path.exists():
        print(f"File not found: {input_path}")
        sys.exit(1)

    text = input_path.read_text(encoding="utf-8")
    validator = SanskritValidator()

    report = validator.validate_document(text, split_mode=split_mode)

    print("=" * 72)
    print("Panini NLP — Document Analysis")
    print("=" * 72)
    print(f"file: {input_path}")
    print(f"split_mode: {report['split_mode']}")
    print(f"segment_count: {report['segment_count']}")
    print(f"summary: {report['summary']}")

    print("\nfirst 3 segments:")
    for seg in report["segments"][:3]:
        result = seg["result"]
        print(f"- [{seg['index']}] {seg['text'][:80]}")
        print(f"  valid={result['is_valid']} patterns={result['grammar_patterns']} suggestions={len(result['suggestions'])}")

    out_json = input_path.with_suffix(input_path.suffix + ".panini_report.json")
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved full JSON report: {out_json}")


if __name__ == "__main__":
    main()
