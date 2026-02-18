"""
Feature encoders for Sanskrit GNN models.

Two encoders are provided:
  - PaniniFeatureEncoder (37-dim): Fine-grained Pāṇinian features
  - UniversalFeatureEncoder (48-dim): UD (Universal Dependencies) tags
"""

import hashlib
import random
from typing import Any, Dict, List

__all__ = ["PaniniFeatureEncoder", "UniversalFeatureEncoder"]


class PaniniFeatureEncoder:
    """
    Encodes a node's linguistic metadata into a 37-dimensional
    feature vector used by the GNN.

    Dimensions breakdown::

        [ 0.. 8]  node type one-hot  (9 types)
        [ 9..11]  category one-hot   (Subanta/Tiṅanta/Avyaya)
        [12..20]  vibhakti one-hot   (8 cases + 1 unknown)
        [21..24]  vacana one-hot     (Sing/Dual/Plur + unknown)
        [25..28]  liṅga one-hot      (M/F/N + unknown)
        [29..32]  puruṣa one-hot     (1st/2nd/3rd + unknown)
        [33..36]  semantic hash      (4 deterministic floats)
    """

    TYPE_MAP = {
        "ACTION": 0, "AGENT": 1, "GOAL": 2, "ENTITY": 3,
        "CONTEXT": 4, "OPERATION": 5, "CONDITION": 6,
        "ADHIKARA": 7, "RULE": 8,
        "Action": 0, "Entity": 3,
    }
    CATEGORY_MAP = {"Subanta": 0, "Tiṅanta": 1, "Avyaya": 2}
    VIBHAKTI_MAP = {
        "Nominative": 0, "Accusative": 1, "Instrumental": 2,
        "Dative": 3, "Ablative": 4, "Genitive": 5,
        "Locative": 6, "Vocative": 7,
    }
    VACANA_MAP = {"Singular": 0, "Dual": 1, "Plural": 2}
    LINGA_MAP = {"Masculine": 0, "Feminine": 1, "Neuter": 2}
    PURUSHA_MAP = {"1st": 0, "2nd": 1, "3rd": 2}

    @property
    def feature_dim(self) -> int:
        return 37

    def encode(self, node_data: Dict[str, Any]) -> List[float]:
        """Return a 37-float feature list for *node_data*."""
        features = [0.0] * 37
        meta = node_data.get("metadata", {})

        # Node type (9 dim)
        ntype = node_data.get("type", "ENTITY")
        t_idx = self.TYPE_MAP.get(ntype, 3)
        if t_idx < 9:
            features[t_idx] = 1.0

        # Category (3 dim)
        cat = meta.get("category", "Avyaya")
        c_idx = self.CATEGORY_MAP.get(cat, 2)
        features[9 + c_idx] = 1.0

        # Vibhakti (9 dim — 8 cases + unknown)
        vib = meta.get("vibhakti") or meta.get("case")
        v_idx = self.VIBHAKTI_MAP.get(vib, 8) if vib else 8
        features[12 + v_idx] = 1.0

        # Vacana (4 dim)
        vac = meta.get("vacana") or meta.get("number")
        vc_idx = self.VACANA_MAP.get(vac, 3) if vac else 3
        features[21 + vc_idx] = 1.0

        # Liṅga (4 dim)
        lin = meta.get("linga") or meta.get("gender")
        l_idx = self.LINGA_MAP.get(lin, 3) if lin else 3
        features[25 + l_idx] = 1.0

        # Puruṣa (4 dim)
        pur = meta.get("purusha") or meta.get("person")
        p_idx = self.PURUSHA_MAP.get(pur, 3) if pur else 3
        features[29 + p_idx] = 1.0

        # Semantic hash (4 dim — deterministic from label)
        label = node_data.get("label", "")
        h = int(hashlib.md5(label.encode()).hexdigest(), 16)
        rng = random.Random(h)
        for i in range(4):
            features[33 + i] = rng.random()

        return features


class UniversalFeatureEncoder:
    """
    Encodes node metadata using Universal Dependencies (UD) tag set
    into a 48-dimensional feature vector.

    Maps both UD tags and Sanskrit-specific terms to a shared space.
    """

    POS_MAP = {
        "NOUN": 0, "VERB": 1, "PROPN": 2, "ADJ": 3, "ADV": 4,
        "ADP": 5, "PRON": 6, "DET": 7, "PART": 8, "NUM": 9,
        "Subanta": 0, "Tiṅanta": 1, "Avyaya": 4,
    }
    DEP_MAP = {
        "nsubj": 0, "obj": 1, "iobj": 2, "csubj": 3,
        "root": 4, "obl": 5, "vocative": 6,
        "KARTA": 0, "KARMA": 1, "SAMPRADANA": 2,
    }
    CASE_MAP = {
        "Nom": 0, "Acc": 1, "Ins": 2, "Dat": 3,
        "Abl": 4, "Gen": 5, "Loc": 6, "Voc": 7,
        "Nominative": 0, "Accusative": 1, "Instrumental": 2,
        "Dative": 3, "Ablative": 4, "Genitive": 5,
        "Locative": 6, "Vocative": 7,
    }
    NUMBER_MAP = {
        "Sing": 0, "Dual": 1, "Plur": 2,
        "Singular": 0, "Plural": 2,
    }

    @property
    def feature_dim(self) -> int:
        return 48

    def encode(self, node_data: Dict[str, Any]) -> List[float]:
        """Return a 48-float feature list for *node_data*."""
        features = [0.0] * 48
        meta = node_data.get("metadata", {})

        cat = meta.get("category", "NOUN")
        if cat in self.POS_MAP:
            features[self.POS_MAP[cat]] = 1.0

        case = meta.get("case", "")
        if case in self.CASE_MAP:
            features[15 + self.CASE_MAP[case]] = 1.0

        number = meta.get("number", "")
        if number in self.NUMBER_MAP:
            features[25 + self.NUMBER_MAP[number]] = 1.0

        dep = meta.get("relation", "")
        if dep in self.DEP_MAP:
            features[30 + self.DEP_MAP[dep]] = 1.0

        return features
