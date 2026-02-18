#!/usr/bin/env python3
"""
Panini NLP — Full Pipeline Demo
Analyzes a Sanskrit sentence through all 5 modules.
"""

from panini_nlp import SanskritValidator, SandhiEngine, MorphologicalAnalyzer, SemanticParser, ChandasAnalyzer, SamasaAnalyzer


def main():
    print("=" * 60)
    print("  Panini NLP — Sanskrit Analysis Pipeline")
    print("=" * 60)

    # === 1. Full pipeline ===
    sentence = "रामः वनम् गच्छति"
    print(f"\n▶ Input: {sentence}\n")

    validator = SanskritValidator()
    result = validator.validate(sentence)

    print(f"  Valid: {result.is_valid}")
    if result.suggestions:
        print("  Suggestions:")
        for s in result.suggestions:
            print(f"    • {s}")
    if result.grammar_patterns.get("morphology"):
        print("  Morphological analysis:")
        for m in result.grammar_patterns["morphology"]:
            print(f"    {m}")
    if result.semantic_graph:
        nodes = result.semantic_graph.get("nodes", [])
        edges = result.semantic_graph.get("edges", [])
        print(f"  Semantic graph: {len(nodes)} nodes, {len(edges)} edges")
        for e in edges:
            print(f"    {e.get('source')} —[{e.get('relation')}]→ {e.get('target')}")

    # === 2. Sandhi ===
    print("\n" + "-" * 60)
    print("▶ Sandhi Engine")
    engine = SandhiEngine()
    pairs = [("देव", "अर्चनम्"), ("महा", "ईश्वरः"), ("गुरु", "उपदेशः")]
    for a, b in pairs:
        r = engine.apply(a, b)
        if r.rule_applied:
            print(f"  {a} + {b} → {r.modified}  ({r.rule_applied.id}: {r.rule_applied.text})")
        else:
            print(f"  {a} + {b} → {r.modified}  (no rule)")

    # === 3. Morphology ===
    print("\n" + "-" * 60)
    print("▶ Morphological Analyzer")
    morph = MorphologicalAnalyzer()
    words = ["रामः", "वनम्", "गच्छति", "देवेन", "फलानि"]
    for w in words:
        analyses = morph.analyze(w)
        for a in analyses[:2]:
            print(
                f"  {w}: stem={a.stem}, category={a.category}, "
                f"vibhakti={a.vibhakti}, vacana={a.vacana}, lakara={a.lakara}"
            )

    # === 4. Chandas ===
    print("\n" + "-" * 60)
    print("▶ Chandas (Prosody)")
    chandas = ChandasAnalyzer()
    verse = "dharmasya tattvam nihitam guhāyām"
    result = chandas.analyze(verse)
    print(f"  Verse: {verse}")
    print(f"  Pattern: {result.pattern}  ({result.syllable_count} syllables)")
    if result.meter_name:
        print(f"  Meter: {result.meter_name}")

    # === 5. Samāsa ===
    print("\n" + "-" * 60)
    print("▶ Samāsa (Compounds)")
    samasa = SamasaAnalyzer()
    compounds = ["yathāvidhi", "pītāmbaram", "mahādeva", "rājapuruṣa"]
    for c in compounds:
        r = samasa.analyze(c)
        if r:
            print(f"  {c}: {r.compound_type}, components={r.constituents}")
        else:
            print(f"  {c}: (no compound detected)")

    print("\n" + "=" * 60)
    print("  Done.")


if __name__ == "__main__":
    main()
