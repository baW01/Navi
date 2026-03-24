from __future__ import annotations

from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    id: str
    lat: float
    lon: float


class GraphEdge(BaseModel):
    segment_id: str
    from_junction_id: str
    to_junction_id: str
    length_m: float
    travel_time_s: float


class RoutingGraphSnapshot(BaseModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


class ValidationReport(BaseModel):
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors
