# Przykładowe uruchomienie (region testowy)

## 1) Import OSM

```bash
navi import-osm tests/fixtures/mini.osm --out .tmp/intermediate --region test-fixture
```

## 2) Budowa grafu

```bash
navi build-graph --input .tmp/intermediate --out .tmp/graph
```

## 3) Routing demo

```bash
navi route --input .tmp/intermediate --start 52.0010,21.0000 --end 52.0010,21.0010 --out .tmp/route.geojson
```

## 4) Eksporty

```bash
navi export-nds-like --input .tmp/intermediate --out .tmp/nds_like
navi export-nds-live-poc --input .tmp/intermediate --out .tmp/nds_live_poc
```

## 5) Walidacja

```bash
navi validate --input .tmp/intermediate
```

## Przykładowe pliki wyjściowe

### nds_like

- `manifest.json`
- `road_network.json`
- `junctions.json`
- `turn_restrictions.json`
- `addresses.json`
- `poi.json`
- `metadata.json`

### nds_live_poc

- `manifest.json`
- `layer_mapping.json`
- `layers/road_network/segments.json`
- `layers/topology/junctions.json`
- `layers/restrictions/turn_restrictions.json`
- `layers/addressing/addresses.json`
- `layers/poi/poi.json`

## Checklista dalszych ulepszeń

- [ ] Lepsza adresacja
- [ ] Incremental updates
- [ ] Tile partitioning
- [ ] CH / faster routing
- [ ] Rendering
- [ ] ADAS layers
