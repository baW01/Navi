PYTHON ?= python

.PHONY: install install-dev test demo clean inspect validate

install:
	$(PYTHON) -m pip install -e .

install-dev:
	$(PYTHON) -m pip install -e .[dev]

test:
	$(PYTHON) -m pytest -q

demo:
	$(PYTHON) -m navi.cli.main import-osm tests/fixtures/mini.osm --out examples/output/intermediate --region test-fixture
	$(PYTHON) -m navi.cli.main build-graph --input examples/output/intermediate --out examples/output/graph
	$(PYTHON) -m navi.cli.main export-nds-like --input examples/output/intermediate --out examples/output/nds_like
	$(PYTHON) -m navi.cli.main export-nds-live-poc --input examples/output/intermediate --out examples/output/nds_live_poc
	$(PYTHON) -m navi.cli.main route --input examples/output/intermediate --start 52.0010,21.0000 --end 52.0010,21.0010 --out examples/output/route.geojson
	$(PYTHON) -m navi.cli.main validate --input examples/output/intermediate

inspect:
	$(PYTHON) -m navi.cli.main inspect --input examples/output/intermediate

validate:
	$(PYTHON) -m navi.cli.main validate --input examples/output/intermediate

clean:
	rm -rf .pytest_cache .tmp examples/output
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
