from pathlib import Path

from navi.ingest.osm_parser import parse_osm
from navi.normalize.canonicalizer import normalize_osm


def test_normalize_builds_junctions_and_segments() -> None:
    raw = parse_osm(Path("tests/fixtures/mini.osm"))
    dataset = normalize_osm(raw, region="test")

    assert len(dataset.junctions) >= 5
    assert len(dataset.road_segments) >= 6
    assert any(segment.oneway for segment in dataset.road_segments if segment.source_way_id == "100")


def test_normalize_extracts_addresses_and_poi() -> None:
    raw = parse_osm(Path("tests/fixtures/mini.osm"))
    dataset = normalize_osm(raw)

    assert len(dataset.addresses) == 1
    assert dataset.addresses[0].street == "Main St"
    assert len(dataset.poi) == 1
    assert dataset.poi[0].subcategory == "fuel"


def test_normalize_turn_restrictions() -> None:
    raw = parse_osm(Path("tests/fixtures/mini.osm"))
    dataset = normalize_osm(raw)

    assert dataset.turn_restrictions
    restriction = dataset.turn_restrictions[0]
    assert restriction.via_junction_id == "2"
    assert restriction.restriction_type == "no_left_turn"
