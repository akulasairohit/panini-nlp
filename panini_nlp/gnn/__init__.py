"""
GNN (Graph Neural Network) module for Sanskrit grammar.

This module is **optional** — it requires PyTorch and PyTorch Geometric.
All other panini-nlp modules work without it.

Install extras::

    pip install panini-nlp[gnn]
    # or manually:
    pip install torch torch_geometric

Provides:
  - SanskritGCN: 3-layer GCN for sentence-graph validity classification
  - TriggerNetwork: MLP predicting which sandhi rule fires for a phoneme pair
  - ConflictNetwork: MLP resolving which of two competing rules wins
  - PaniniFeatureEncoder: Encodes linguistic features into 37-dim vectors
  - UniversalFeatureEncoder: UD-tag-based 48-dim encoder
"""

from panini_nlp.gnn.features import PaniniFeatureEncoder, UniversalFeatureEncoder
from panini_nlp.gnn.models import (
    SanskritGCN,
    TriggerNetwork,
    ConflictNetwork,
)
from panini_nlp.gnn.inference import GNNInference

__all__ = [
    "SanskritGCN",
    "TriggerNetwork",
    "ConflictNetwork",
    "PaniniFeatureEncoder",
    "UniversalFeatureEncoder",
    "GNNInference",
]
