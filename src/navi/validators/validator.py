from __future__ import annotations

from navi.models.canonical import CanonicalDataset
from navi.models.graph import ValidationReport

KNOWN_ROAD_CLASSES = {
    "motorway",
    "trunk",
    "primary",
    "secondary",
    "tertiary",
    "unclassified",
    "residential",
    "service",
    "living_street",
    "track",
}


def validate_dataset(dataset: CanonicalDataset) -> ValidationReport:
    report = ValidationReport()

    junction_ids = {junction.id for junction in dataset.junctions}
    segment_ids = {segment.id for segment in dataset.road_segments}

    for segment in dataset.road_segments:
        if not segment.geometry:
            report.errors.append(f"Segment {segment.id} nie ma geometrii.")

        if segment.from_junction_id not in junction_ids:
            report.errors.append(
                f"Segment {segment.id} ma nieistniejący from_junction_id={segment.from_junction_id}."
            )
        if segment.to_junction_id not in junction_ids:
            report.errors.append(f"Segment {segment.id} ma nieistniejący to_junction_id={segment.to_junction_id}.")

        if segment.road_class not in KNOWN_ROAD_CLASSES:
            report.warnings.append(
                f"Segment {segment.id} ma nieznaną klasę drogi: {segment.road_class}."
            )

        if segment.name is not None and segment.name.strip() == "":
            report.warnings.append(f"Segment {segment.id} ma pustą nazwę ulicy.")

    for junction in dataset.junctions:
        dangling_segment_refs = [sid for sid in junction.connected_segment_ids if sid not in segment_ids]
        if dangling_segment_refs:
            report.errors.append(
                f"Junction {junction.id} ma dangling connected_segment_ids: {dangling_segment_refs}"
            )
        if not junction.connected_segment_ids:
            report.warnings.append(f"Junction {junction.id} nie ma połączeń topologicznych.")

    for restriction in dataset.turn_restrictions:
        if restriction.from_segment_id not in segment_ids:
            report.errors.append(
                f"Restriction {restriction.id} ma nieistniejący from_segment_id={restriction.from_segment_id}."
            )
        if restriction.to_segment_id not in segment_ids:
            report.errors.append(
                f"Restriction {restriction.id} ma nieistniejący to_segment_id={restriction.to_segment_id}."
            )
        if restriction.via_junction_id and restriction.via_junction_id not in junction_ids:
            report.errors.append(
                f"Restriction {restriction.id} ma nieistniejący via_junction_id={restriction.via_junction_id}."
            )
        if not restriction.restriction_type:
            report.warnings.append(f"Restriction {restriction.id} nie ma restriction_type.")

    return report
