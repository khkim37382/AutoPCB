from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ProjectSpec:
    name: str
    type: str
    raw: Dict[str, Any]

    @property
    def power(self) -> Dict[str, Any]:
        return self.raw.get("power", {})

    @property
    def decoupling(self) -> List[Dict[str, Any]]:
        return self.raw.get("decoupling", [])
