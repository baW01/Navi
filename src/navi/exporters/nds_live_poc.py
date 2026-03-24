from __future__ import annotations

from pathlib import Path

from navi.models.canonical import CanonicalDataset
from navi.utils.io import write_json


def export_nds_live_poc(dataset: CanonicalDataset, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    layers_dir = output_dir / "layers"
    road_dir = layers_dir / "road_network"
    topology_dir = layers_dir / "topology"
    restrictions_dir = layers_dir / "restrictions"
    address_dir = layers_dir / "addressing"
    poi_dir = layers_dir / "poi"

    for path in (road_dir, topology_dir, restrictions_dir, address_dir, poi_dir):
        path.mkdir(parents=True, exist_ok=True)

    write_json(road_dir / "segments.json", [segment.model_dump(mode="json") for segment in dataset.road_segments])
    write_json(topology_dir / "junctions.json", [junction.model_dump(mode="json") for junction in dataset.junctions])
    write_json(
        restrictions_dir / "turn_restrictions.json",
        [item.model_dump(mode="json") for item in dataset.turn_restrictions],
    )
    write_json(address_dir / "addresses.json", [item.model_dump(mode="json") for item in dataset.addresses])
    write_json(poi_dir / "poi.json", [item.model_dump(mode="json") for item in dataset.poi])

    mapping = {
        "note": "To jest jawny PoC warstwowy inspirowany NDS.Live. To NIE jest pełna implementacja zamkniętych/binary OEM specyfikacji.",
        "conceptual_mapping": {
            "RoadNetworkLayer": "layers/road_network/segments.json",
            "TopologyLayer": "layers/topology/junctions.json",
            "TurnRestrictionLayer": "layers/restrictions/turn_restrictions.json",
            "AddressLayer": "layers/addressing/addresses.json",
            "POILayer": "layers/poi/poi.json",
        },
    }
    write_json(output_dir / "layer_mapping.json", mapping)

    manifest = {
        "format": "nds_live_poc",
        "version": "0.1.0",
        "compliance": {
            "full_nds_live_binary_compatibility": False,
            "reason": "Brak kompletnej publicznej specyfikacji implementacyjnej dla pełnej zgodności binarnej.",
        },
        "source": dataset.metadata.model_dump(mode="json"),
    }
    write_json(output_dir / "manifest.json", manifest)
