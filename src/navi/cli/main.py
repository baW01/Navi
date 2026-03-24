from __future__ import annotations

from pathlib import Path

import typer

from navi.exporters.nds_like import export_nds_like
from navi.exporters.nds_live_poc import export_nds_live_poc
from navi.ingest.osm_parser import parse_osm
from navi.normalize.canonicalizer import normalize_osm
from navi.routing.graph_builder import build_graph
from navi.routing.router import compute_route, parse_lat_lon, save_route_geojson
from navi.utils.io import (
    CANONICAL_FILE,
    load_canonical,
    save_canonical,
    save_graph,
    save_validation,
)
from navi.utils.logging import configure_logging
from navi.validators.validator import validate_dataset

app = typer.Typer(help="Navi: OSM -> canonical automotive navigation -> NDS-like/NDS.Live PoC")


@app.command("import-osm")
def import_osm(
    pbf_path: Path = typer.Argument(..., exists=True, help="Ścieżka do pliku .pbf lub .osm"),
    out: Path = typer.Option(..., "--out", help="Katalog wyjściowy"),
    region: str | None = typer.Option(None, "--region", help="Nazwa regionu"),
    verbose: bool = typer.Option(False, "--verbose"),
) -> None:
    """Importuje OSM i zapisuje canonical schema."""
    configure_logging(verbose)
    raw = parse_osm(pbf_path)
    dataset = normalize_osm(raw, region=region)
    output_path = save_canonical(out, dataset)
    typer.echo(f"Zapisano canonical dataset: {output_path}")


@app.command("build-graph")
def build_graph_command(
    input_dir: Path = typer.Option(..., "--input", exists=True),
    out: Path = typer.Option(..., "--out"),
) -> None:
    """Buduje graf routingu z canonical schema."""
    dataset = load_canonical(input_dir)
    _, snapshot = build_graph(dataset)
    output_path = save_graph(out, snapshot)
    typer.echo(f"Zapisano graf routingu: {output_path}")


@app.command("export-nds-like")
def export_nds_like_command(
    input_dir: Path = typer.Option(..., "--input", exists=True),
    out: Path = typer.Option(..., "--out"),
) -> None:
    """Eksportuje do otwartego formatu nds_like."""
    dataset = load_canonical(input_dir)
    export_nds_like(dataset, out)
    typer.echo(f"Eksport nds_like gotowy: {out}")


@app.command("export-nds-live-poc")
def export_nds_live_poc_command(
    input_dir: Path = typer.Option(..., "--input", exists=True),
    out: Path = typer.Option(..., "--out"),
) -> None:
    """Eksportuje do warstwowego nds_live_poc."""
    dataset = load_canonical(input_dir)
    export_nds_live_poc(dataset, out)
    typer.echo(f"Eksport nds_live_poc gotowy: {out}")


@app.command("validate")
def validate_command(input_dir: Path = typer.Option(..., "--input", exists=True)) -> None:
    """Waliduje canonical dataset."""
    dataset = load_canonical(input_dir)
    report = validate_dataset(dataset)
    save_validation(input_dir, report)

    typer.echo(f"Validation errors: {len(report.errors)}")
    typer.echo(f"Validation warnings: {len(report.warnings)}")
    for error in report.errors:
        typer.echo(f"ERROR: {error}")
    for warning in report.warnings:
        typer.echo(f"WARN: {warning}")

    if not report.is_valid:
        raise typer.Exit(code=1)


@app.command("route")
def route_command(
    input_dir: Path = typer.Option(..., "--input", exists=True),
    start: str = typer.Option(..., "--start", help="Punkt startu w formacie lat,lon"),
    end: str = typer.Option(..., "--end", help="Punkt końca w formacie lat,lon"),
    out: Path = typer.Option(..., "--out", help="Plik wyjściowy GeoJSON"),
    algorithm: str = typer.Option("dijkstra", "--algorithm", help="dijkstra|astar"),
    weight: str = typer.Option("travel_time_s", "--weight", help="travel_time_s|length_m"),
) -> None:
    """Wyznacza przykładową trasę A->B i zapisuje GeoJSON."""
    dataset = load_canonical(input_dir)
    route_geojson = compute_route(dataset, parse_lat_lon(start), parse_lat_lon(end), algorithm=algorithm, weight=weight)
    save_route_geojson(route_geojson, out)
    typer.echo(f"Zapisano trasę: {out}")


@app.command("inspect")
def inspect_command(input_dir: Path = typer.Option(..., "--input", exists=True)) -> None:
    """Pokazuje podstawowe statystyki zbioru canonical."""
    dataset = load_canonical(input_dir)
    typer.echo(f"Canonical file: {input_dir / CANONICAL_FILE}")
    typer.echo(f"Junctions: {len(dataset.junctions)}")
    typer.echo(f"Road segments: {len(dataset.road_segments)}")
    typer.echo(f"Turn restrictions: {len(dataset.turn_restrictions)}")
    typer.echo(f"Addresses: {len(dataset.addresses)}")
    typer.echo(f"POI: {len(dataset.poi)}")
    typer.echo(f"Region: {dataset.metadata.region}")
    typer.echo(f"BBox: {dataset.metadata.bounding_box}")


if __name__ == "__main__":
    app()
