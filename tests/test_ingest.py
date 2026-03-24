from pathlib import Path

from navi.ingest.osm_parser import parse_osm


def test_parse_osm_xml_extracts_entities() -> None:
    fixture = Path("tests/fixtures/mini.osm")
    raw = parse_osm(fixture)

    assert len(raw.nodes) >= 7
    assert len(raw.ways) == 2
    assert len(raw.restrictions) == 1
    assert raw.restrictions[0].restriction_type == "no_left_turn"
