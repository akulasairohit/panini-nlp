"""
Kāraka-based Semantic Network Builder for Sanskrit.

Parses Sanskrit sentences into directed semantic graphs where:
  - Each verb becomes an Action node
  - Each noun/participant becomes an Entity node
  - Edges represent Kāraka relations (Agent, Object, Instrument, …)

Inspired by Briggs (1985) "Knowledge Representation in Sanskrit and AI".
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .morphology import MorphologicalAnalyzer, MorphAnalysis

__all__ = ["SemanticNode", "SemanticEdge", "SemanticGraph", "SemanticParser"]


@dataclass
class SemanticNode:
    """A node in the semantic network."""
    id: str
    label: str
    type: str  # "Action" | "Entity"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SemanticEdge:
    """A directed edge (relation) in the semantic network."""
    source_id: str
    target_id: str
    relation: str  # "agent", "object", "instrument", …
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SemanticGraph:
    """A lightweight semantic graph (no external dependencies)."""
    nodes: List[SemanticNode] = field(default_factory=list)
    edges: List[SemanticEdge] = field(default_factory=list)

    def add_node(self, node: SemanticNode) -> None:
        self.nodes.append(node)

    def add_edge(self, edge: SemanticEdge) -> None:
        self.edges.append(edge)

    def to_dict(self) -> Dict[str, Any]:
        """Serializable dictionary representation."""
        return {
            "nodes": [
                {"id": n.id, "label": n.label, "type": n.type, "metadata": n.metadata}
                for n in self.nodes
            ],
            "edges": [
                {"source": e.source_id, "target": e.target_id,
                 "relation": e.relation, "metadata": e.metadata}
                for e in self.edges
            ],
        }

    def summary(self) -> str:
        """Human-readable summary of the graph."""
        lines = [f"SemanticGraph: {len(self.nodes)} nodes, {len(self.edges)} edges"]
        for e in self.edges:
            src = next((n for n in self.nodes if n.id == e.source_id), None)
            tgt = next((n for n in self.nodes if n.id == e.target_id), None)
            if src and tgt:
                lines.append(f"  {src.label} --[{e.relation}]--> {tgt.label}")
        return "\n".join(lines)


_ROLE_SIMPLIFY = {
    "Kartā":      "agent",
    "Karma":      "object",
    "Karaṇa":     "instrument",
    "Sampradāna": "recipient",
    "Apādāna":    "source",
    "Adhikaraṇa": "location",
    "Sambandha":  "related_to",
    "Sambodhana": "address",
}


class SemanticParser:
    """
    Parse Sanskrit sentences into Kāraka-based semantic graphs.

    >>> parser = SemanticParser()
    >>> g = parser.parse("रामः वनं गच्छति")
    >>> print(g.summary())
    """

    def __init__(self, analyzer: Optional[MorphologicalAnalyzer] = None) -> None:
        self.analyzer = analyzer or MorphologicalAnalyzer()

    def parse(self, sentence: str) -> SemanticGraph:
        """Parse a space-separated Sanskrit sentence into a SemanticGraph."""
        graph = SemanticGraph()
        words = sentence.split()

        action_node: Optional[SemanticNode] = None
        participants: List[tuple] = []  # (node, role_str)

        for word in words:
            analyses = self.analyzer.analyze(word)
            if not analyses:
                continue
            analysis = analyses[0]  # take first (most likely)

            if analysis.category == "Tiṅanta":
                node = SemanticNode(
                    id=f"action_{word}",
                    label=f"{analysis.stem} ({word})",
                    type="Action",
                    metadata={
                        "category": analysis.category,
                        "lakara": analysis.lakara or "",
                        "purusha": analysis.purusha or "",
                        "vacana": analysis.vacana or "",
                    },
                )
                graph.add_node(node)
                action_node = node

            elif analysis.category == "Subanta":
                full_role = MorphologicalAnalyzer.get_karaka(analysis)
                simple = self._simplify(full_role)
                node = SemanticNode(
                    id=f"entity_{word}",
                    label=f"{analysis.stem} ({word})",
                    type="Entity",
                    metadata={
                        "role": full_role,
                        "category": analysis.category,
                        "vibhakti": analysis.vibhakti or "",
                        "vacana": analysis.vacana or "",
                    },
                )
                graph.add_node(node)
                participants.append((node, simple))
            else:
                node = SemanticNode(
                    id=f"token_{word}",
                    label=word,
                    type="Entity",
                    metadata={"category": analysis.category},
                )
                graph.add_node(node)

        # Link participants → action
        if action_node:
            for pnode, role in participants:
                graph.add_edge(SemanticEdge(
                    source_id=action_node.id,
                    target_id=pnode.id,
                    relation=role,
                ))

        return graph

    @staticmethod
    def _simplify(full_role: str) -> str:
        for key, val in _ROLE_SIMPLIFY.items():
            if key in full_role:
                return val
        return "unknown"
