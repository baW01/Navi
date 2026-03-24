from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from navi.models.canonical import (
    Address,
    CanonicalDataset,
    Junction,
    Metadata,
    POI,
    RoadSegment,
    TurnRestriction,
)
from navi.models.raw_osm import RawNode, RawOSMExtract

POI_KEYS = {"amenity", "shop", "tourism"}
POI_VALUES = {"fuel", "parking", "hospital", "restaurant", "police", "pharmacy"}


@dataclass(slots=True)
class _SegmentRef:
    segment_id: str
    source_way_id: str
    from_junction_id: str
    to_junction_id: str


def normalize_osm(raw: RawOSMExtract, region: str | None = None) -> CanonicalDataset:
    used_node_ids = _collect_road_node_ids(raw)
    junctions = _build_junctions(raw.nodes, used_node_ids)
    segments, segment_refs = _build_segments(raw)
    _attach_segment_references(junctions, segments)
    restrictions = _build_turn_restrictions(raw, segment_refs)
    addresses = _extract_addresses(raw.nodes)
    pois = _extract_poi(raw.nodes)
    metadata = Metadata(
        source_data=raw.source_path,
        bounding_box=_compute_bbox(raw.nodes.values()),
        region=region,
    )

    return CanonicalDataset(
        junctions=list(junctions.values()),
        road_segments=segments,
        turn_restrictions=restrictions,
        addresses=addresses,
        poi=pois,
        metadata=metadata,
    )


def _collect_road_node_ids(raw: RawOSMExtract) -> set[str]:
    road_node_ids: set[str] = set()
    for way in raw.ways:
        road_node_ids.update(way.node_ids)
    return road_node_ids


def _build_junctions(nodes: dict[str, RawNode], used_node_ids: set[str]) -> dict[str, Junction]:
    junctions: dict[str, Junction] = {}
    for node_id in used_node_ids:
        node = nodes.get(node_id)
        if not node:
            continue

        junctions[node_id] = Junction(id=node_id, lat=node.lat, lon=node.lon)
    return junctions


def _build_segments(raw: RawOSMExtract) -> tuple[list[RoadSegment], list[_SegmentRef]]:
    segments: list[RoadSegment] = []
    refs: list[_SegmentRef] = []

    for way in raw.ways:
        tags = way.tags
        oneway = _is_oneway(tags)
        for idx in range(len(way.node_ids) - 1):
            from_id = way.node_ids[idx]
            to_id = way.node_ids[idx + 1]
            from_node = raw.nodes.get(from_id)
            to_node = raw.nodes.get(to_id)
            if not from_node or not to_node:
                continue

            base_kwargs = {
                "name": tags.get("name"),
                "ref": tags.get("ref"),
                "road_class": tags.get("highway", "unknown"),
                "oneway": oneway,
                "maxspeed": _parse_maxspeed(tags.get("maxspeed")),
                "lanes": _safe_int(tags.get("lanes")),
                "surface": tags.get("surface"),
                "access_car": _access_car(tags),
                "toll": _is_yes(tags.get("toll")),
                "bridge": _is_yes(tags.get("bridge")),
                "tunnel": _is_yes(tags.get("tunnel")),
                "source_way_id": way.id,
            }

            seg_id = f"{way.id}:{idx}:fwd"
            segments.append(
                RoadSegment(
                    id=seg_id,
                    from_junction_id=from_id,
                    to_junction_id=to_id,
                    geometry=[[from_node.lon, from_node.lat], [to_node.lon, to_node.lat]],
                    **base_kwargs,
                )
            )
            refs.append(
                _SegmentRef(
                    segment_id=seg_id,
                    source_way_id=way.id,
                    from_junction_id=from_id,
                    to_junction_id=to_id,
                )
            )

            if oneway:
                continue

            rev_id = f"{way.id}:{idx}:rev"
            segments.append(
                RoadSegment(
                    id=rev_id,
                    from_junction_id=to_id,
                    to_junction_id=from_id,
                    geometry=[[to_node.lon, to_node.lat], [from_node.lon, from_node.lat]],
                    **base_kwargs,
                )
            )
            refs.append(
                _SegmentRef(
                    segment_id=rev_id,
                    source_way_id=way.id,
                    from_junction_id=to_id,
                    to_junction_id=from_id,
                )
            )

    return segments, refs


def _attach_segment_references(junctions: dict[str, Junction], segments: list[RoadSegment]) -> None:
    for segment in segments:
        if segment.from_junction_id in junctions:
            junctions[segment.from_junction_id].connected_segment_ids.append(segment.id)
        if segment.to_junction_id in junctions:
            junctions[segment.to_junction_id].connected_segment_ids.append(segment.id)


def _build_turn_restrictions(raw: RawOSMExtract, refs: list[_SegmentRef]) -> list[TurnRestriction]:
    restrictions: list[TurnRestriction] = []
    for restriction in raw.restrictions:
        if restriction.via_node_id:
            from_candidates = [
                ref
                for ref in refs
                if ref.source_way_id == restriction.from_way_id and ref.to_junction_id == restriction.via_node_id
            ]
            to_candidates = [
                ref
                for ref in refs
                if ref.source_way_id == restriction.to_way_id and ref.from_junction_id == restriction.via_node_id
            ]

            for from_ref in from_candidates:
                for to_ref in to_candidates:
                    restrictions.append(
                        TurnRestriction(
                            id=f"{restriction.id}:{from_ref.segment_id}:{to_ref.segment_id}",
                            from_segment_id=from_ref.segment_id,
                            via_junction_id=restriction.via_node_id,
                            to_segment_id=to_ref.segment_id,
                            restriction_type=restriction.restriction_type,
                        )
                    )

        elif restriction.via_way_id:
            via_candidates = [ref for ref in refs if ref.source_way_id == restriction.via_way_id]
            from_candidates = [ref for ref in refs if ref.source_way_id == restriction.from_way_id]
            to_candidates = [ref for ref in refs if ref.source_way_id == restriction.to_way_id]

            for from_ref in from_candidates:
                for via_ref in via_candidates:
                    if from_ref.to_junction_id != via_ref.from_junction_id:
                        continue
                    for to_ref in to_candidates:
                        if via_ref.to_junction_id != to_ref.from_junction_id:
                            continue
                        restrictions.append(
                            TurnRestriction(
                                id=f"{restriction.id}:{from_ref.segment_id}:{to_ref.segment_id}",
                                from_segment_id=from_ref.segment_id,
                                via_segment_id=via_ref.segment_id,
                                to_segment_id=to_ref.segment_id,
                                restriction_type=restriction.restriction_type,
                            )
                        )

    return restrictions


def _extract_addresses(nodes: dict[str, RawNode]) -> list[Address]:
    addresses: list[Address] = []
    for node in nodes.values():
        tags = node.tags
        if not any(key.startswith("addr:") for key in tags):
            continue

        addresses.append(
            Address(
                id=node.id,
                house_number=tags.get("addr:housenumber"),
                street=tags.get("addr:street"),
                city=tags.get("addr:city"),
                postcode=tags.get("addr:postcode"),
                country=tags.get("addr:country"),
                lat=node.lat,
                lon=node.lon,
            )
        )
    return addresses


def _extract_poi(nodes: dict[str, RawNode]) -> list[POI]:
    pois: list[POI] = []
    for node in nodes.values():
        tags = node.tags
        category = None
        subcategory = None

        for key in POI_KEYS:
            if key in tags:
                category = key
                subcategory = tags.get(key)
                break

        if not category:
            for value in POI_VALUES:
                if tags.get("amenity") == value:
                    category = "amenity"
                    subcategory = value
                    break

        if not category:
            continue

        pois.append(
            POI(
                id=node.id,
                name=tags.get("name"),
                category=category,
                subcategory=subcategory,
                lat=node.lat,
                lon=node.lon,
            )
        )
    return pois


def _compute_bbox(nodes: list[RawNode]) -> list[float] | None:
    if not nodes:
        return None
    lats = [node.lat for node in nodes]
    lons = [node.lon for node in nodes]
    return [min(lons), min(lats), max(lons), max(lats)]


def _is_yes(raw_value: str | None) -> bool:
    if raw_value is None:
        return False
    return raw_value.lower() in {"yes", "true", "1"}


def _is_oneway(tags: dict[str, str]) -> bool:
    oneway = tags.get("oneway", "").lower()
    if oneway in {"yes", "1", "true"}:
        return True
    if tags.get("junction") == "roundabout":
        return True
    return False


def _parse_maxspeed(raw_value: str | None) -> int | None:
    if not raw_value:
        return None
    digits = "".join(character for character in raw_value if character.isdigit())
    if not digits:
        return None
    return int(digits)


def _safe_int(raw_value: str | None) -> int | None:
    if not raw_value:
        return None
    try:
        return int(raw_value)
    except ValueError:
        return None


def _access_car(tags: dict[str, str]) -> bool:
    for key in ("access", "motor_vehicle", "vehicle"):
        value = tags.get(key)
        if value is None:
            continue
        low = value.lower()
        if low in {"no", "private", "agricultural", "forestry"}:
            return False
        if low in {"yes", "permissive", "designated"}:
            return True
    return True
