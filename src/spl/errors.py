from dataclasses import dataclass
from typing import Optional


@dataclass
class Diagnostic:
    """
    Structured diagnostic produced by the checker.

    Fields:
      - kind: short machine-friendly kind (e.g. 'UndeclaredVariable')
      - message: human-friendly message
      - node_id: AST node id where the issue was detected (if available)
      - scope_path: optional textual scope path to help debugging
    """
    kind: str
    message: str
    node_id: int = -1
    scope_path: Optional[str] = None

    def __str__(self) -> str:
        node = f" (node #{self.node_id})" if self.node_id is not None and self.node_id != -1 else ""
        scope = f" [{self.scope_path}]" if self.scope_path else ""
        return f"{self.kind}: {self.message}{node}{scope}"
