from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class Junction(BaseModel):
    id: str
    lat: float
    lon: float
    connected_segment_ids: list[str] = Field(default_factory=list)


class RoadSegment(BaseModel):
    id: str
    from_junction_id: str
    to_junction_id: str
    geometry: list[list[float]]
    name: str | None = None
    ref: str | None = None
    road_class: str
    oneway: bool
    maxspeed: int | None = None
    lanes: int | None = None
    surface: str | None = None
    access_car: bool = True
    toll: bool = False
    bridge: bool = False
    tunnel: bool = False
    source_way_id: str | None = None


class TurnRestriction(BaseModel):
    id: str
    from_segment_id: str
    via_junction_id: str | None = None
    via_segment_id: str | None = None
    to_segment_id: str
    restriction_type: str


class Address(BaseModel):
    id: str
    house_number: str | None = None
    street: str | None = None
    city: str | None = None
    postcode: str | None = None
    country: str | None = None
    lat: float
    lon: float


class POI(BaseModel):
    id: str
    name: str | None = None
    category: str
    subcategory: str | None = None
    lat: float
    lon: float


class Metadata(BaseModel):
    source_data: str
    imported_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    bounding_box: list[float] | None = None
    region: str | None = None
    pipeline_version: str = "0.1.0"


class CanonicalDataset(BaseModel):
    junctions: list[Junction] = Field(default_factory=list)
    road_segments: list[RoadSegment] = Field(default_factory=list)
    turn_restrictions: list[TurnRestriction] = Field(default_factory=list)
    addresses: list[Address] = Field(default_factory=list)
    poi: list[POI] = Field(default_factory=list)
    metadata: Metadata
