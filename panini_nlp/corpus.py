"""
Corpus access for full Aṣṭādhyāyī and Dhātupāṭha bundled in panini_nlp.

This module does not claim full executable derivation for all rules.
It provides structured access to the full textual corpus so users can
lookup/search every bundled sūtra and dhātu from Python.
"""

from dataclasses import dataclass
from functools import lru_cache
from importlib.resources import files
import re
from typing import List, Optional

__all__ = [
    "SutraEntry",
    "DhatuEntry",
    "AshtadhyayiCorpus",
    "DhatupathaCorpus",
    "SanskritCorpus",
]

_DEVANAGARI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")


@dataclass(frozen=True)
class SutraEntry:
    id: str
    id_ascii: str
    text: str
    raw: str


@dataclass(frozen=True)
class DhatuEntry:
    code: str
    code_ascii: str
    dhatu: str
    meaning: str
    raw: str


def _to_ascii_digits(value: str) -> str:
    return value.translate(_DEVANAGARI_DIGITS)


@lru_cache(maxsize=1)
def _load_ashtadhyayi_entries() -> List[SutraEntry]:
    path = files("panini_nlp.data").joinpath("Ashtadhyayi.txt")
    content = path.read_text(encoding="utf-8")

    entries: List[SutraEntry] = []
    pattern = re.compile(r"^([०-९0-9]+\.[०-९0-9]+\.[०-९0-9]+)\s+(.+?)\s*।+$")

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("॥"):
            continue
        match = pattern.match(line)
        if not match:
            continue

        sutra_id = match.group(1)
        sutra_text = match.group(2).strip()
        entries.append(
            SutraEntry(
                id=sutra_id,
                id_ascii=_to_ascii_digits(sutra_id),
                text=sutra_text,
                raw=line,
            )
        )

    return entries


@lru_cache(maxsize=1)
def _load_dhatupatha_entries() -> List[DhatuEntry]:
    path = files("panini_nlp.data").joinpath("Dhatupatha.txt")
    content = path.read_text(encoding="utf-8")

    entries: List[DhatuEntry] = []
    numbered_pattern = re.compile(r"^([०-९0-9]+\.[०-९0-9]+)\s+(.+)$")

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("अथ ") or line.startswith("॥"):
            continue

        match = numbered_pattern.match(line)
        if not match:
            continue

        code = match.group(1)
        tail = match.group(2).strip()
        tail = tail.split("॥", 1)[0].strip()
        tail = tail.rstrip("।").strip()
        if not tail:
            continue

        parts = tail.split(maxsplit=1)
        dhatu = parts[0].strip()
        meaning = parts[1].strip() if len(parts) > 1 else ""
        entries.append(
            DhatuEntry(
                code=code,
                code_ascii=_to_ascii_digits(code),
                dhatu=dhatu,
                meaning=meaning,
                raw=line,
            )
        )

    return entries


class AshtadhyayiCorpus:
    """Structured access to all bundled Aṣṭādhyāyī sūtras."""

    def __init__(self) -> None:
        self._entries = _load_ashtadhyayi_entries()

    @property
    def count(self) -> int:
        return len(self._entries)

    def all(self) -> List[SutraEntry]:
        return list(self._entries)

    def get(self, sutra_id: str) -> Optional[SutraEntry]:
        target = sutra_id.strip()
        target_ascii = _to_ascii_digits(target)
        for entry in self._entries:
            if entry.id == target or entry.id_ascii == target_ascii:
                return entry
        return None

    def search(self, query: str, limit: int = 20) -> List[SutraEntry]:
        needle = query.strip().lower()
        if not needle:
            return []

        found: List[SutraEntry] = []
        for entry in self._entries:
            hay = f"{entry.id} {entry.id_ascii} {entry.text}".lower()
            if needle in hay:
                found.append(entry)
                if len(found) >= limit:
                    break
        return found


class DhatupathaCorpus:
    """Structured access to all bundled Dhātupāṭha entries."""

    def __init__(self) -> None:
        self._entries = _load_dhatupatha_entries()

    @property
    def count(self) -> int:
        return len(self._entries)

    def all(self) -> List[DhatuEntry]:
        return list(self._entries)

    def get(self, code: str) -> Optional[DhatuEntry]:
        target = code.strip()
        target_ascii = _to_ascii_digits(target)
        for entry in self._entries:
            if entry.code == target or entry.code_ascii == target_ascii:
                return entry
        return None

    def search(self, query: str, limit: int = 20) -> List[DhatuEntry]:
        needle = query.strip().lower()
        if not needle:
            return []

        found: List[DhatuEntry] = []
        for entry in self._entries:
            hay = f"{entry.code} {entry.code_ascii} {entry.dhatu} {entry.meaning}".lower()
            if needle in hay:
                found.append(entry)
                if len(found) >= limit:
                    break
        return found

    def find_roots(self, surface: str, limit: int = 20) -> List[DhatuEntry]:
        needle = surface.strip()
        if not needle:
            return []

        found: List[DhatuEntry] = []
        for entry in self._entries:
            if needle in entry.dhatu:
                found.append(entry)
                if len(found) >= limit:
                    break
        return found


class SanskritCorpus:
    """Convenience wrapper exposing both Aṣṭādhyāyī and Dhātupāṭha."""

    def __init__(self) -> None:
        self.ashtadhyayi = AshtadhyayiCorpus()
        self.dhatupatha = DhatupathaCorpus()
