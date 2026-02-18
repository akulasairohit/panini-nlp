from pathlib import Path
import json

from panini_nlp.meaning import SanskritMeaningEngine


def main() -> None:
    input_path = Path(
        "/Users/sairohit/Sanskrit-2/_DOCUMENTS/10_Canonical_Texts_caraka_data_dcs_raw_corpora_Spandakārikā.txt"
    )

    text = input_path.read_text(encoding="utf-8")
    engine = SanskritMeaningEngine()
    report = engine.analyze_document_meaning(text, split_mode="verse", meaning_mode="fluent")

    report_dict = report.to_dict()

    json_path = Path(str(input_path) + ".meaning_report.json")
    json_path.write_text(json.dumps(report_dict, ensure_ascii=False, indent=2), encoding="utf-8")

    mode_breakdown = report.summary.get("meaning_mode_breakdown", {})
    has_only_heuristic = (
        mode_breakdown.get("heuristic_fallback", 0) == report.segment_count
    )

    txt_suffix = ".heuristic_gloss.txt" if has_only_heuristic else ".translation.txt"
    txt_path = Path(str(input_path) + txt_suffix)
    lines: list[str] = []
    lines.append("Spandakarika — Line-by-line Meaning (panini-nlp)")
    lines.append("")
    if has_only_heuristic:
        lines.append("WARNING: No model translator configured. This is heuristic gloss, not authoritative translation.")
        lines.append("")
    lines.append("Segments: " + str(report.segment_count))
    lines.append("Summary: " + str(report.summary))
    lines.append("")

    for seg in report.segments:
        lines.append("[" + str(seg.index) + "] " + seg.source)
        lines.append("Meaning: " + seg.meaning)
        lines.append("Confidence: " + str(seg.confidence))
        lines.append("")

    txt_path.write_text("\n".join(lines), encoding="utf-8")

    print("OK")
    print(str(json_path))
    print(str(txt_path))
    print("segments=" + str(report.segment_count))


if __name__ == "__main__":
    main()
