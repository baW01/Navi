from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class RawNode(BaseModel):
    id: str
    lat: float
    lon: float
    tags: dict[str, str] = Field(default_factory=dict)


class RawWay(BaseModel):
    id: str
    node_ids: list[str]
    tags: dict[str, str] = Field(default_factory=dict)


class RawTurnRestriction(BaseModel):
    id: str
    from_way_id: str
    to_way_id: str
    via_node_id: str | None = None
    via_way_id: str | None = None
    restriction_type: str


class RawOSMExtract(BaseModel):
    nodes: dict[str, RawNode] = Field(default_factory=dict)
    ways: list[RawWay] = Field(default_factory=list)
    restrictions: list[RawTurnRestriction] = Field(default_factory=list)
    source_path: str
