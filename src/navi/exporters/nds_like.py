from __future__ import annotations

from pathlib import Path

from navi.models.canonical import CanonicalDataset
from navi.utils.io import write_json


def export_nds_like(dataset: CanonicalDataset, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    write_json(output_dir / "junctions.json", [item.model_dump(mode="json") for item in dataset.junctions])
    write_json(
        output_dir / "road_network.json",
        [item.model_dump(mode="json") for item in dataset.road_segments],
    )
    write_json(
        output_dir / "turn_restrictions.json",
        [item.model_dump(mode="json") for item in dataset.turn_restrictions],
    )
    write_json(output_dir / "addresses.json", [item.model_dump(mode="json") for item in dataset.addresses])
    write_json(output_dir / "poi.json", [item.model_dump(mode="json") for item in dataset.poi])
    write_json(output_dir / "metadata.json", dataset.metadata.model_dump(mode="json"))

    manifest = {
        "format": "nds_like",
        "version": "0.1.0",
        "entities": {
            "junctions": len(dataset.junctions),
            "road_segments": len(dataset.road_segments),
            "turn_restrictions": len(dataset.turn_restrictions),
            "addresses": len(dataset.addresses),
            "poi": len(dataset.poi),
        },
    }
    write_json(output_dir / "manifest.json", manifest)
