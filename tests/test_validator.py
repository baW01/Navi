from pathlib import Path

from navi.ingest.osm_parser import parse_osm
from navi.normalize.canonicalizer import normalize_osm
from navi.validators.validator import validate_dataset


def test_validate_dataset_ok_for_fixture() -> None:
    dataset = normalize_osm(parse_osm(Path("tests/fixtures/mini.osm")))
    report = validate_dataset(dataset)
    assert report.is_valid
