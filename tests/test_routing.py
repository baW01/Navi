from pathlib import Path

from navi.ingest.osm_parser import parse_osm
from navi.normalize.canonicalizer import normalize_osm
from navi.routing.graph_builder import build_graph
from navi.routing.router import compute_route


def test_build_graph_has_nodes_and_edges() -> None:
    raw = parse_osm(Path("tests/fixtures/mini.osm"))
    dataset = normalize_osm(raw)

    graph, snapshot = build_graph(dataset)

    assert graph.number_of_nodes() == len(dataset.junctions)
    assert graph.number_of_edges() == len(dataset.road_segments)
    assert len(snapshot.edges) == len(dataset.road_segments)


def test_route_geojson() -> None:
    raw = parse_osm(Path("tests/fixtures/mini.osm"))
    dataset = normalize_osm(raw)

    route_geojson = compute_route(dataset, start=(52.0010, 21.0000), end=(52.0010, 21.0010))

    assert route_geojson["type"] == "FeatureCollection"
    geometry = route_geojson["features"][0]["geometry"]
    assert geometry["type"] == "LineString"
    assert len(geometry["coordinates"]) >= 2
