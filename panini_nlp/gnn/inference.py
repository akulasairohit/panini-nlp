"""
GNN inference engine — load pre-trained models and run predictions.

Handles model loading, device management, and provides a single
``GNNInference`` class for all three GNN layers.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

__all__ = ["GNNInference"]

try:
    import torch

    _HAS_TORCH = True
except ImportError:
    _HAS_TORCH = False


class GNNInference:
    """
    Load pre-trained GNN models and run inference.

    Parameters
    ----------
    models_dir : str or Path
        Directory containing ``.pth`` weight files.
    device : str
        ``"cpu"`` or ``"cuda"`` (default ``"cpu"``).

    Example
    -------
    >>> gi = GNNInference("path/to/models")
    >>> gi.predict_trigger(0, 5)  # phoneme indices
    {'predicted_rule': 2, 'probabilities': [...]}
    """

    def __init__(
        self,
        models_dir: Optional[str] = None,
        device: str = "cpu",
    ) -> None:
        if not _HAS_TORCH:
            raise ImportError("PyTorch is required.  pip install torch")

        self.device = torch.device(device)

        # Default: look for models/ dir next to this file
        if models_dir is None:
            models_dir = str(
                Path(__file__).parent.parent / "models"
            )
        self.models_dir = Path(models_dir)

        # Lazily loaded models
        self._validity_model = None
        self._trigger_model = None
        self._conflict_model = None

    # ── validity (Layer 1) ───────────────────────────────────────────────

    def load_validity_model(
        self,
        path: Optional[str] = None,
        input_dim: int = 37,
        hidden_channels: int = 64,
    ) -> None:
        """Load the SanskritGCN validity model."""
        from panini_nlp.gnn.models import SanskritGCN

        model = SanskritGCN(input_dim, hidden_channels, num_classes=1)
        ckpt = path or str(self.models_dir / "sanskrit_gnn_mega.pth")
        if os.path.isfile(ckpt):
            state = torch.load(ckpt, map_location=self.device, weights_only=True)
            model.load_state_dict(state)
        model.to(self.device).eval()
        self._validity_model = model

    # ── trigger (Layer 2) ────────────────────────────────────────────────

    def load_trigger_model(
        self,
        path: Optional[str] = None,
        vocab_size: int = 11,
        hidden_dim: int = 32,
        num_classes: int = 6,
    ) -> None:
        """Load the TriggerNetwork sandhi-rule predictor."""
        from panini_nlp.gnn.models import TriggerNetwork

        model = TriggerNetwork(vocab_size, hidden_dim, num_classes)
        ckpt = path or str(self.models_dir / "layer2_trigger_model.pth")
        if os.path.isfile(ckpt):
            state = torch.load(ckpt, map_location=self.device, weights_only=True)
            model.load_state_dict(state)
        model.to(self.device).eval()
        self._trigger_model = model

    def predict_trigger(self, c1_idx: int, c2_idx: int) -> Dict[str, Any]:
        """Predict which sandhi rule fires for phoneme pair ``(c1, c2)``."""
        if self._trigger_model is None:
            self.load_trigger_model()
        t1 = torch.tensor([c1_idx], device=self.device)
        t2 = torch.tensor([c2_idx], device=self.device)
        with torch.no_grad():
            logits = self._trigger_model(t1, t2)
            probs = torch.softmax(logits, dim=1)
        pred = int(torch.argmax(probs, dim=1).item())
        return {
            "predicted_rule": pred,
            "probabilities": probs[0].tolist(),
        }

    # ── conflict (Layer 3) ───────────────────────────────────────────────

    def load_conflict_model(
        self,
        path: Optional[str] = None,
        num_rules: int = 6,
        hidden_dim: int = 64,
    ) -> None:
        """Load the ConflictNetwork rule-priority resolver."""
        from panini_nlp.gnn.models import ConflictNetwork

        model = ConflictNetwork(num_rules, hidden_dim)
        ckpt = path or str(self.models_dir / "layer3_conflict_model.pth")
        if os.path.isfile(ckpt):
            state = torch.load(ckpt, map_location=self.device, weights_only=True)
            model.load_state_dict(state)
        model.to(self.device).eval()
        self._conflict_model = model

    def predict_conflict(self, r1_idx: int, r2_idx: int) -> Dict[str, Any]:
        """Predict which rule wins in a conflict between rule r1 and rule r2."""
        if self._conflict_model is None:
            self.load_conflict_model()
        t1 = torch.tensor([r1_idx], device=self.device)
        t2 = torch.tensor([r2_idx], device=self.device)
        with torch.no_grad():
            logits = self._conflict_model(t1, t2)
            probs = torch.softmax(logits, dim=1)
        winner = int(torch.argmax(probs, dim=1).item())
        return {
            "winner": f"rule_{r1_idx}" if winner == 0 else f"rule_{r2_idx}",
            "winner_index": winner,
            "probabilities": probs[0].tolist(),
        }
