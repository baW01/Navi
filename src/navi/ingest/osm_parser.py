from __future__ import annotations

import logging
from pathlib import Path
from xml.etree import ElementTree as ET

from navi.models.raw_osm import RawNode, RawOSMExtract, RawTurnRestriction, RawWay

LOGGER = logging.getLogger(__name__)

ROAD_TAG = "highway"


def parse_osm(input_path: Path) -> RawOSMExtract:
    suffix = input_path.suffix.lower()
    if suffix == ".osm":
        return _parse_osm_xml(input_path)

    return _parse_with_pyosmium(input_path)


def _parse_osm_xml(input_path: Path) -> RawOSMExtract:
    tree = ET.parse(input_path)
    root = tree.getroot()

    nodes: dict[str, RawNode] = {}
    ways: list[RawWay] = []
    restrictions: list[RawTurnRestriction] = []

    for node in root.findall("node"):
        node_id = node.attrib["id"]
        tags = {tag.attrib["k"]: tag.attrib["v"] for tag in node.findall("tag")}
        nodes[node_id] = RawNode(
            id=node_id,
            lat=float(node.attrib["lat"]),
            lon=float(node.attrib["lon"]),
            tags=tags,
        )

    for way in root.findall("way"):
        way_id = way.attrib["id"]
        node_ids = [nd.attrib["ref"] for nd in way.findall("nd")]
        tags = {tag.attrib["k"]: tag.attrib["v"] for tag in way.findall("tag")}
        if ROAD_TAG in tags:
            ways.append(RawWay(id=way_id, node_ids=node_ids, tags=tags))

    for rel in root.findall("relation"):
        tags = {tag.attrib["k"]: tag.attrib["v"] for tag in rel.findall("tag")}
        if tags.get("type") != "restriction":
            continue

        from_way_id = None
        to_way_id = None
        via_node_id = None
        via_way_id = None

        for member in rel.findall("member"):
            role = member.attrib.get("role")
            member_type = member.attrib.get("type")
            ref = member.attrib.get("ref")
            if role == "from" and member_type == "way":
                from_way_id = ref
            elif role == "to" and member_type == "way":
                to_way_id = ref
            elif role == "via" and member_type == "node":
                via_node_id = ref
            elif role == "via" and member_type == "way":
                via_way_id = ref

        if from_way_id and to_way_id and (via_node_id or via_way_id):
            restrictions.append(
                RawTurnRestriction(
                    id=rel.attrib["id"],
                    from_way_id=from_way_id,
                    to_way_id=to_way_id,
                    via_node_id=via_node_id,
                    via_way_id=via_way_id,
                    restriction_type=tags.get("restriction", "unknown"),
                )
            )

    return RawOSMExtract(nodes=nodes, ways=ways, restrictions=restrictions, source_path=str(input_path))


def _parse_with_pyosmium(input_path: Path) -> RawOSMExtract:
    try:
        import osmium
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "Pakiet 'osmium' (pyosmium) jest wymagany do parsowania .pbf. "
            "Zainstaluj zależności: pip install -e ."
        ) from exc

    class OSMHandler(osmium.SimpleHandler):
        def __init__(self) -> None:
            super().__init__()
            self.nodes: dict[str, RawNode] = {}
            self.ways: list[RawWay] = []
            self.restrictions: list[RawTurnRestriction] = []

        def node(self, node: osmium.osm.Node) -> None:
            tags = {tag.k: tag.v for tag in node.tags}
            self.nodes[str(node.id)] = RawNode(
                id=str(node.id),
                lat=float(node.location.lat),
                lon=float(node.location.lon),
                tags=tags,
            )

        def way(self, way: osmium.osm.Way) -> None:
            tags = {tag.k: tag.v for tag in way.tags}
            if ROAD_TAG not in tags:
                return

            node_ids = [str(n.ref) for n in way.nodes]
            self.ways.append(RawWay(id=str(way.id), node_ids=node_ids, tags=tags))

        def relation(self, relation: osmium.osm.Relation) -> None:
            tags = {tag.k: tag.v for tag in relation.tags}
            if tags.get("type") != "restriction":
                return

            from_way_id = None
            to_way_id = None
            via_node_id = None
            via_way_id = None

            for member in relation.members:
                if member.role == "from" and member.type == "w":
                    from_way_id = str(member.ref)
                elif member.role == "to" and member.type == "w":
                    to_way_id = str(member.ref)
                elif member.role == "via" and member.type == "n":
                    via_node_id = str(member.ref)
                elif member.role == "via" and member.type == "w":
                    via_way_id = str(member.ref)

            if from_way_id and to_way_id and (via_node_id or via_way_id):
                self.restrictions.append(
                    RawTurnRestriction(
                        id=str(relation.id),
                        from_way_id=from_way_id,
                        to_way_id=to_way_id,
                        via_node_id=via_node_id,
                        via_way_id=via_way_id,
                        restriction_type=tags.get("restriction", "unknown"),
                    )
                )

    handler = OSMHandler()
    LOGGER.info("Parsing OSM file: %s", input_path)
    handler.apply_file(str(input_path), locations=True)

    return RawOSMExtract(
        nodes=handler.nodes,
        ways=handler.ways,
        restrictions=handler.restrictions,
        source_path=str(input_path),
    )
