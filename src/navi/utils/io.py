from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel

from navi.models.canonical import CanonicalDataset
from navi.models.graph import RoutingGraphSnapshot, ValidationReport

CANONICAL_FILE = "canonical.json"
GRAPH_FILE = "graph.json"
VALIDATION_FILE = "validation_report.json"

try:
    import orjson
except ImportError:  # pragma: no cover
    orjson = None


def _dumps(data: Any) -> bytes:
    if orjson:
        return orjson.dumps(data, option=orjson.OPT_INDENT_2)

    import json

    return json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")


def _loads(raw: bytes) -> Any:
    if orjson:
        return orjson.loads(raw)

    import json

    return json.loads(raw.decode("utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_dumps(payload))


def write_model(path: Path, model: BaseModel) -> None:
    write_json(path, model.model_dump(mode="json"))


def read_json(path: Path) -> Any:
    return _loads(path.read_bytes())


def load_canonical(input_dir: Path) -> CanonicalDataset:
    raw = read_json(input_dir / CANONICAL_FILE)
    return CanonicalDataset.model_validate(raw)


def save_canonical(output_dir: Path, dataset: CanonicalDataset) -> Path:
    output_path = output_dir / CANONICAL_FILE
    write_model(output_path, dataset)
    return output_path


def load_graph(input_dir: Path) -> RoutingGraphSnapshot:
    raw = read_json(input_dir / GRAPH_FILE)
    return RoutingGraphSnapshot.model_validate(raw)


def save_graph(output_dir: Path, graph: RoutingGraphSnapshot) -> Path:
    output_path = output_dir / GRAPH_FILE
    write_model(output_path, graph)
    return output_path


def save_validation(output_dir: Path, report: ValidationReport) -> Path:
    output_path = output_dir / VALIDATION_FILE
    write_model(output_path, report)
    return output_path
