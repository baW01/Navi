from pathlib import Path

from navi.exporters.nds_like import export_nds_like
from navi.exporters.nds_live_poc import export_nds_live_poc
from navi.ingest.osm_parser import parse_osm
from navi.normalize.canonicalizer import normalize_osm


def test_export_nds_like(tmp_path: Path) -> None:
    dataset = normalize_osm(parse_osm(Path("tests/fixtures/mini.osm")))
    out = tmp_path / "nds_like"

    export_nds_like(dataset, out)

    assert (out / "manifest.json").exists()
    assert (out / "road_network.json").exists()
    assert (out / "junctions.json").exists()


def test_export_nds_live_poc(tmp_path: Path) -> None:
    dataset = normalize_osm(parse_osm(Path("tests/fixtures/mini.osm")))
    out = tmp_path / "nds_live_poc"

    export_nds_live_poc(dataset, out)

    assert (out / "manifest.json").exists()
    assert (out / "layer_mapping.json").exists()
    assert (out / "layers" / "road_network" / "segments.json").exists()
