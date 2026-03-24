from __future__ import annotations

import math

import networkx as nx

from navi.models.canonical import CanonicalDataset, RoadSegment
from navi.models.graph import GraphEdge, GraphNode, RoutingGraphSnapshot

DEFAULT_SPEED_KMH = {
    "motorway": 120,
    "trunk": 100,
    "primary": 80,
    "secondary": 60,
    "tertiary": 50,
    "residential": 40,
    "service": 20,
}


def build_graph(dataset: CanonicalDataset) -> tuple[nx.DiGraph, RoutingGraphSnapshot]:
    graph = nx.DiGraph()
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []

    for junction in dataset.junctions:
        graph.add_node(junction.id, lat=junction.lat, lon=junction.lon)
        nodes.append(GraphNode(id=junction.id, lat=junction.lat, lon=junction.lon))

    restricted = {
        (restriction.from_segment_id, restriction.to_segment_id)
        for restriction in dataset.turn_restrictions
        if restriction.restriction_type.startswith("no_")
    }

    for segment in dataset.road_segments:
        length_m = segment_length_m(segment)
        speed_kmh = segment.maxspeed or DEFAULT_SPEED_KMH.get(segment.road_class, 50)
        travel_time_s = length_m / (speed_kmh * 1000 / 3600)

        graph.add_edge(
            segment.from_junction_id,
            segment.to_junction_id,
            segment_id=segment.id,
            length_m=length_m,
            travel_time_s=travel_time_s,
            geometry=segment.geometry,
        )

        edges.append(
            GraphEdge(
                segment_id=segment.id,
                from_junction_id=segment.from_junction_id,
                to_junction_id=segment.to_junction_id,
                length_m=length_m,
                travel_time_s=travel_time_s,
            )
        )

    graph.graph["turn_restrictions"] = list(restricted)

    return graph, RoutingGraphSnapshot(nodes=nodes, edges=edges)


def segment_length_m(segment: RoadSegment) -> float:
    if len(segment.geometry) < 2:
        return 0.0

    total = 0.0
    for idx in range(len(segment.geometry) - 1):
        lon1, lat1 = segment.geometry[idx]
        lon2, lat2 = segment.geometry[idx + 1]
        total += haversine_m(lat1, lon1, lat2, lon2)
    return total


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6_371_000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c
