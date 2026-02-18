from dataclasses import dataclass
from typing import Callable, Dict, Optional

@dataclass
class Sutra:
    id: str
    text: str
    description: str = ""
    source: str = "Ashtadhyayi"

class RuleRegistry:
    def __init__(self):
        self._rules: Dict[str, Sutra] = {}
        self._implementations: Dict[str, Callable] = {}

    def register(self, id: str, text: str = ""):
        def decorator(func: Callable):
            self._rules[id] = Sutra(id=id, text=text, description=func.__doc__ or "")
            self._implementations[id] = func
            return func
        return decorator

    def get(self, id: str) -> Optional[Sutra]:
        return self._rules.get(id)

    def get_implementation(self, id: str) -> Optional[Callable]:
        return self._implementations.get(id)

    def __iter__(self):
        return iter(self._rules.values())

# Global registry
registry = RuleRegistry()

# Auto-import generated modules to populate registry
from . import (
    adhyaya_1, adhyaya_2, adhyaya_3, adhyaya_4,
    adhyaya_5, adhyaya_6, adhyaya_7, adhyaya_8
)
