from __future__ import annotations

from pathlib import Path

import networkx as nx

from navi.models.canonical import CanonicalDataset
from navi.routing.graph_builder import build_graph, haversine_m
from navi.utils.io import write_json


def parse_lat_lon(raw_value: str) -> tuple[float, float]:
    try:
        lat_str, lon_str = raw_value.split(",", maxsplit=1)
        return float(lat_str.strip()), float(lon_str.strip())
    except Exception as exc:  # pragma: no cover
        raise ValueError(f"Niepoprawny format punktu: '{raw_value}'. Oczekiwane: lat,lon") from exc


def nearest_junction(dataset: CanonicalDataset, lat: float, lon: float) -> str:
    best_id = None
    best_distance = float("inf")
    for junction in dataset.junctions:
        distance = haversine_m(lat, lon, junction.lat, junction.lon)
        if distance < best_distance:
            best_distance = distance
            best_id = junction.id
    if not best_id:
        raise ValueError("Brak junctions w zbiorze danych.")
    return best_id


def compute_route(
    dataset: CanonicalDataset,
    start: tuple[float, float],
    end: tuple[float, float],
    algorithm: str = "dijkstra",
    weight: str = "travel_time_s",
) -> dict:
    graph, _ = build_graph(dataset)
    start_node = nearest_junction(dataset, start[0], start[1])
    end_node = nearest_junction(dataset, end[0], end[1])

    if algorithm == "astar":
        path = nx.astar_path(
            graph,
            start_node,
            end_node,
            heuristic=lambda n1, n2: _heuristic(graph, n1, n2),
            weight=weight,
        )
    else:
        path = nx.shortest_path(graph, start_node, end_node, weight=weight, method="dijkstra")

    coordinates = _path_coordinates(graph, path)
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": coordinates},
                "properties": {
                    "start_node": start_node,
                    "end_node": end_node,
                    "algorithm": algorithm,
                    "weight": weight,
                    "node_path": path,
                },
            }
        ],
    }


def save_route_geojson(route_geojson: dict, output_path: Path) -> None:
    write_json(output_path, route_geojson)


def _heuristic(graph: nx.DiGraph, node1: str, node2: str) -> float:
    n1 = graph.nodes[node1]
    n2 = graph.nodes[node2]
    return haversine_m(n1["lat"], n1["lon"], n2["lat"], n2["lon"])


def _path_coordinates(graph: nx.DiGraph, path: list[str]) -> list[list[float]]:
    coordinates: list[list[float]] = []
    for idx in range(len(path) - 1):
        edge = graph[path[idx]][path[idx + 1]]
        geometry = edge.get("geometry", [])
        if idx == 0:
            coordinates.extend(geometry)
        else:
            coordinates.extend(geometry[1:])
    return coordinates
