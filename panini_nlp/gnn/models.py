"""
GNN model architectures for Sanskrit grammar analysis.

All models require ``torch`` and ``torch_geometric``.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    from torch_geometric.nn import GCNConv, global_mean_pool

    _HAS_PYG = True
except ImportError:
    _HAS_PYG = False

__all__ = ["SanskritGCN", "TriggerNetwork", "ConflictNetwork"]


# ═══════════════════════════════════════════════════════════════════════════
# Layer 1 — Graph-level validity classifier
# ═══════════════════════════════════════════════════════════════════════════


class SanskritGCN(nn.Module):
    """
    3-layer GCN for classifying sentence graphs as grammatically
    valid vs. invalid (binary).

    Architecture::

        GCNConv → ReLU → GCNConv → ReLU → GCNConv → ReLU
        → global_mean_pool → Dropout → Linear → sigmoid

    Parameters
    ----------
    input_dim : int
        Node feature dimensionality (37 for PaniniFeatureEncoder).
    hidden_channels : int
        Width of hidden GCN layers.
    num_classes : int
        Output dimensionality (default 1 for binary).
    """

    def __init__(
        self, input_dim: int = 37, hidden_channels: int = 64, num_classes: int = 1
    ) -> None:
        if not _HAS_PYG:
            raise ImportError(
                "PyTorch Geometric is required.  "
                "pip install torch_geometric"
            )
        super().__init__()
        self.conv1 = GCNConv(input_dim, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, hidden_channels)
        self.conv3 = GCNConv(hidden_channels, hidden_channels)
        self.lin = nn.Linear(hidden_channels, num_classes)

    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        batch: torch.Tensor,
    ) -> torch.Tensor:
        x = F.relu(self.conv1(x, edge_index))
        x = F.dropout(x, p=0.2, training=self.training)
        x = F.relu(self.conv2(x, edge_index))
        x = F.relu(self.conv3(x, edge_index))
        x = global_mean_pool(x, batch)
        x = F.dropout(x, p=0.5, training=self.training)
        x = self.lin(x)
        return torch.sigmoid(x)


# ═══════════════════════════════════════════════════════════════════════════
# Layer 2 — Sandhi trigger prediction
# ═══════════════════════════════════════════════════════════════════════════


class TriggerNetwork(nn.Module):
    """
    Given two phoneme indices (the last char of word₁ and the first
    char of word₂), predict which sandhi rule fires.

    Architecture::

        Embedding(vocab, 16) × 2 → concat → FC₁ → FC₂ → FC₃

    Parameters
    ----------
    vocab_size : int
        Size of the phoneme vocabulary (default 11).
    hidden_dim : int
        Hidden layer width (default 32).
    num_classes : int
        Number of sandhi rule classes (default 6).
    """

    def __init__(
        self, vocab_size: int = 11, hidden_dim: int = 32, num_classes: int = 6
    ) -> None:
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, 16)
        self.fc1 = nn.Linear(16 * 2, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, num_classes)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)

    def forward(
        self, c1_idx: torch.Tensor, c2_idx: torch.Tensor
    ) -> torch.Tensor:
        e1 = self.embedding(c1_idx)
        e2 = self.embedding(c2_idx)
        x = torch.cat([e1, e2], dim=1)
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x


# ═══════════════════════════════════════════════════════════════════════════
# Layer 3 — Rule-conflict resolution
# ═══════════════════════════════════════════════════════════════════════════


class ConflictNetwork(nn.Module):
    """
    Given two competing rule indices, predict which rule wins.

    Architecture::

        Embedding(num_rules, 32) × 2 → concat → FC₁ → FC₂ → FC₃ (2-class)

    Parameters
    ----------
    num_rules : int
        Total number of rules in the vocabulary (default 6).
    hidden_dim : int
        Hidden layer width (default 64).
    """

    def __init__(self, num_rules: int = 6, hidden_dim: int = 64) -> None:
        super().__init__()
        self.rule_emb = nn.Embedding(num_rules, 32)
        self.fc1 = nn.Linear(32 * 2, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, 2)  # [Win_R1, Win_R2]
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)

    def forward(
        self, r1_idx: torch.Tensor, r2_idx: torch.Tensor
    ) -> torch.Tensor:
        e1 = self.rule_emb(r1_idx)
        e2 = self.rule_emb(r2_idx)
        x = torch.cat([e1, e2], dim=1)
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x
