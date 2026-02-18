"""
Piṅgala Compression Engine — .meru format.

Implements "Sūtra Compression": dictionary-encode repetitive string
fields, pack with msgpack, and compress with zlib.

Requires: msgpack (``pip install msgpack``).
"""

from typing import Any, Dict, List, Optional
import json
import os
import zlib

__all__ = ["MeruCompressor"]

try:
    import msgpack
    _HAS_MSGPACK = True
except ImportError:
    _HAS_MSGPACK = False


class MeruCompressor:
    """
    Compress / decompress structured data using the .meru format.

    The algorithm:
      1. **DNA extraction** — find string columns whose unique-value count
         is less than the row count (dictionary-encoding candidates).
      2. **Tokenize** — replace string values with integer indices.
      3. **Pack** — serialize with msgpack (binary, dense).
      4. **Compress** — zlib level-9 for maximum compression.

    Decompression reverses every step losslessly.

    >>> comp = MeruCompressor()
    >>> data = [{"state": "AP", "city": "Hyd"}, {"state": "AP", "city": "Viz"}]
    >>> blob = comp.compress(data, "test")
    >>> comp.decompress(blob) == data
    True
    """

    def __init__(self) -> None:
        if not _HAS_MSGPACK:
            raise ImportError(
                "msgpack is required for compression.  "
                "Install it with:  pip install msgpack"
            )

    # ── compress ─────────────────────────────────────────────────────────────

    def compress(self, data: List[Dict[str, Any]], dataset_name: str = "data") -> bytes:
        """Compress a list of flat dicts into a .meru binary blob."""
        if not data:
            return self._pack_and_deflate({
                "meta": {"type": "meru_sutra_v1", "name": dataset_name},
                "schema": [],
                "dna": {},
                "stream": [],
            })

        keys = list(data[0].keys())

        # 1 — Identify dictionary-encoding candidates (string columns)
        vocab_registry: Dict[str, Dict[str, int]] = {}
        reverse_vocab: Dict[str, List[str]] = {}

        for k in keys:
            sample = data[0].get(k)
            if not isinstance(sample, str):
                continue
            unique = set(row.get(k, "") for row in data)
            if len(unique) < len(data):
                sorted_vals = sorted(unique)
                vocab_registry[k] = {v: i for i, v in enumerate(sorted_vals)}
                reverse_vocab[k] = sorted_vals

        # 2 — Tokenize
        stream: List[List[Any]] = []
        for row in data:
            new_row: List[Any] = []
            for k in keys:
                val = row.get(k)
                if k in vocab_registry:
                    new_row.append(vocab_registry[k].get(val, 0))  # type: ignore[arg-type]
                else:
                    new_row.append(val)
            stream.append(new_row)

        seed = {
            "meta": {"type": "meru_sutra_v1", "name": dataset_name},
            "schema": keys,
            "dna": reverse_vocab,
            "stream": stream,
        }
        return self._pack_and_deflate(seed)

    # ── decompress ───────────────────────────────────────────────────────────

    def decompress(self, meru_bytes: bytes) -> List[Dict[str, Any]]:
        """Decompress a .meru blob back to a list of dicts."""
        try:
            packed = zlib.decompress(meru_bytes)
        except zlib.error:
            return []

        seed = msgpack.unpackb(packed, raw=False)
        keys: List[str] = seed["schema"]
        dna: Dict[str, List[str]] = seed["dna"]
        stream: List[List[Any]] = seed["stream"]

        result: List[Dict[str, Any]] = []
        for row_ids in stream:
            obj: Dict[str, Any] = {}
            for idx, k in enumerate(keys):
                val = row_ids[idx]
                if k in dna:
                    obj[k] = dna[k][val]
                else:
                    obj[k] = val
            result.append(obj)
        return result

    # ── file helpers ─────────────────────────────────────────────────────────

    def save(self, data: List[Dict[str, Any]], filepath: str) -> int:
        """Compress *data* and write to *filepath*. Returns byte-count."""
        blob = self.compress(data, os.path.basename(filepath))
        with open(filepath, "wb") as f:
            f.write(blob)
        return len(blob)

    def load(self, filepath: str) -> List[Dict[str, Any]]:
        """Load a .meru file and return decompressed data."""
        with open(filepath, "rb") as f:
            blob = f.read()
        return self.decompress(blob)

    # ── internals ────────────────────────────────────────────────────────────

    @staticmethod
    def _pack_and_deflate(obj: Any) -> bytes:
        packed = msgpack.packb(obj, use_bin_type=True)
        return zlib.compress(packed, level=9)

    # ── comparison helpers ───────────────────────────────────────────────────

    @staticmethod
    def compare_sizes(data: List[Dict[str, Any]], meru_bytes: bytes) -> Dict[str, Any]:
        """Return a dict comparing JSON vs .meru sizes and compression ratio."""
        json_size = len(json.dumps(data, ensure_ascii=False).encode("utf-8"))
        meru_size = len(meru_bytes)
        return {
            "json_bytes": json_size,
            "meru_bytes": meru_size,
            "ratio": round(meru_size / json_size, 4) if json_size else 0,
            "savings_pct": round((1 - meru_size / json_size) * 100, 2) if json_size else 0,
        }
