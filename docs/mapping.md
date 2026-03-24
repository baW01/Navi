# Mapowanie OSM -> Canonical -> NDS-like / NDS.Live PoC

| OSM | Canonical | nds_like | nds_live_poc |
|---|---|---|---|
| `way[highway=*]` | `RoadSegment` | `road_network.json` | `layers/road_network/segments.json` |
| `node` (w drogach) | `Junction` | `junctions.json` | `layers/topology/junctions.json` |
| `relation[type=restriction]` | `TurnRestriction` | `turn_restrictions.json` | `layers/restrictions/turn_restrictions.json` |
| `node[addr:*]` | `Address` | `addresses.json` | `layers/addressing/addresses.json` |
| `node[amenity/shop/tourism]` | `POI` | `poi.json` | `layers/poi/poi.json` |
| metadane importu | `Metadata` | `metadata.json` + `manifest.json` | `manifest.json` + `layer_mapping.json` |

## Uwagi o zgodności NDS.Live

- Ten projekt dostarcza **koncepcyjne mapowanie warstw**.
- Pełna zgodność binarna NDS.Live nie jest implementowana bez kompletnej i publicznej specyfikacji wykonawczej.
- Nie zgadujemy formatu binarnego OEM.
