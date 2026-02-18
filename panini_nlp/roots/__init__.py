from dataclasses import dataclass
from typing import Callable, Dict, Optional

@dataclass
class Dhatu:
    id: str  # e.g. "1.1"
    ganapath_code: str # e.g. "bhvadi"
    root: str # e.g. "bhū"
    meaning: str # e.g. "sattāyām"
    pada: str # "P" | "A" | "U"
    set_anit: str # "S" | "A" | "V"

class RootRegistry:
    def __init__(self):
        self._roots: Dict[str, Dhatu] = {}
        self._implementations: Dict[str, Callable] = {}

    def register(self, id: str, root: str, meaning: str, gana: str):
        def decorator(func: Callable):
            self._roots[id] = Dhatu(
                id=id, 
                ganapath_code=gana,
                root=root, 
                meaning=meaning,
                pada="Unknown", # To be populated
                set_anit="Unknown"
            )
            self._implementations[id] = func
            return func
        return decorator

    def get(self, id: str) -> Optional[Dhatu]:
        return self._roots.get(id)

    def __iter__(self):
        return iter(self._roots.values())

# Global registry
registry = RootRegistry()

# Auto-import generated modules to populate registry
from . import (
    gana_1_bhvadi, gana_2_adadi, gana_3_juhotyadi,
    gana_4_divadi, gana_5_svadi, gana_6_tudadi,
    gana_7_rudhadi, gana_8_tanadi, gana_9_kryadi,
    gana_10_curadi
)
