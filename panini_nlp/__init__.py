"""
panini-nlp — Sanskrit NLP library grounded in Pāṇinian grammar.

Modules
-------
- sandhi     : Sandhi (euphonic junction) engine with Aṣṭādhyāyī rule citations
- morphology : Morphological analyzer (subanta / tiṅanta)
- semantics  : Kāraka-based semantic graph builder
- chandas    : Piṅgala prosody / meter analyzer
- samasa     : Compound (samāsa) analyzer
- compression: .meru format compressor (dictionary + msgpack + zlib)
- validator  : Full NLP pipeline orchestrator
- gnn        : Optional GNN models (requires torch + torch_geometric)
"""

__version__ = "0.2.0"

from panini_nlp.sandhi import SandhiEngine
from panini_nlp.morphology import MorphologicalAnalyzer
from panini_nlp.semantics import SemanticParser
from panini_nlp.chandas import ChandasAnalyzer
from panini_nlp.samasa import SamasaAnalyzer
from panini_nlp.validator import SanskritValidator, ValidationResult
from panini_nlp.meaning import SanskritMeaningEngine, MeaningReport, MeaningSegment
from panini_nlp.corpus import (
    SutraEntry,
    DhatuEntry,
    AshtadhyayiCorpus,
    DhatupathaCorpus,
    SanskritCorpus,
)

__all__ = [
    "SandhiEngine",
    "MorphologicalAnalyzer",
    "SemanticParser",
    "ChandasAnalyzer",
    "SamasaAnalyzer",
    "SanskritValidator",
    "ValidationResult",
    "SanskritMeaningEngine",
    "MeaningReport",
    "MeaningSegment",
    "SutraEntry",
    "DhatuEntry",
    "AshtadhyayiCorpus",
    "DhatupathaCorpus",
    "SanskritCorpus",
    "__version__",
]

# Optional imports — don't fail if torch is missing
try:
    from panini_nlp.compression import MeruCompressor
    __all__.append("MeruCompressor")
except ImportError:
    pass
