# Navi

Modułowy pipeline CLI w Pythonie do przetwarzania danych OpenStreetMap (`.pbf` / `.osm`) do jawnego, kanonicznego modelu pośredniego dla nawigacji samochodowej oraz eksportu do:

- `nds_like` (otwarty format JSON do testów),
- `nds_live_poc` (PoC koncepcyjnie zgodny z warstwami NDS.Live, bez zgadywania zamkniętych specyfikacji).

> Projekt celowo **nie** wykonuje reverse engineeringu firmware/OEM, nie omija DRM/podpisów i działa wyłącznie na legalnych danych OSM.

## Funkcjonalności

- import OSM (`.pbf` przez `pyosmium`, `.osm` XML jako fallback testowy),
- ekstrakcja i normalizacja: drogi, skrzyżowania, ograniczenia skrętu, oneway, maxspeed, nazwy, adresy, POI,
- budowa skierowanego grafu routingu,
- demo routingu (nearest-node + Dijkstra/A*),
- eksport do `nds_like` i `nds_live_poc`,
- walidacja topologii i referencji,
- CLI obejmujące pełny pipeline.

## Instalacja

Wymagany Python `3.11+`.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Wersja developerska z testami:

```bash
pip install -e .[dev]
```

## Automatyzacja

```bash
make install-dev
make test
make demo
make inspect
```

CI (GitHub Actions) znajduje się w `.github/workflows/ci.yml` i uruchamia testy dla Python 3.11 i 3.12.

## CLI

```bash
navi import-osm region.osm.pbf --out data/intermediate
navi build-graph --input data/intermediate --out data/graph
navi export-nds-like --input data/intermediate --out data/nds_like
navi export-nds-live-poc --input data/intermediate --out data/nds_live_poc
navi validate --input data/intermediate
navi route --input data/intermediate --start 52.2297,21.0122 --end 52.2351,21.0059 --out route.geojson
navi inspect --input data/intermediate
```

## Szybki przykład (fixture testowy)

```bash
navi import-osm tests/fixtures/mini.osm --out .tmp/intermediate
navi build-graph --input .tmp/intermediate --out .tmp/graph
navi route --input .tmp/intermediate --start 52.0000,21.0000 --end 52.0010,21.0010 --out .tmp/route.geojson
navi export-nds-like --input .tmp/intermediate --out .tmp/nds_like
navi export-nds-live-poc --input .tmp/intermediate --out .tmp/nds_live_poc
navi validate --input .tmp/intermediate
```

## Struktura projektu

- `src/navi/ingest` – parser OSM,
- `src/navi/normalize` – normalizacja do canonical schema,
- `src/navi/routing` – graf i wyznaczanie trasy,
- `src/navi/exporters` – eksportery,
- `src/navi/validators` – walidacja,
- `src/navi/models` – modele danych,
- `src/navi/cli` – komendy CLI,
- `tests` – testy jednostkowe i integracyjne,
- `docs` – architektura, schema, mapowanie,
- `examples` – przykładowe artefakty.

## Ograniczenia

- pełna zgodność NDS.Live wymaga publicznie niedostępnych/niepełnych specyfikacji implementacyjnych,
- `nds_live_poc` jest świadomie PoC warstwowym,
- parser XML fallback służy głównie testom; produkcyjnie rekomendowany `.pbf` + `pyosmium`.

## Legal and compliance

- Brak reverse engineeringu formatów OEM.
- Brak obchodzenia DRM, podpisów cyfrowych, aktywacji, zabezpieczeń SD.
- Brak generowania wsadów do zamkniętych systemów wymagających obejścia zabezpieczeń.
- Źródło danych: legalne dane OSM.
- Brak użycia danych z Google Maps i innych źródeł z niezgodną licencją eksportową.

## Dalsze kierunki rozwoju

- lepsza adresacja,
- incremental updates,
- tile partitioning,
- CH / faster routing,
- rendering,
- ADAS layers.