# 🇵🇱 INSTRUKCJA: Przetwarzanie Danych OSM Polski

## ✅ Co zostało przygotowane

Kompletny pipeline do przetwarzania danych OpenStreetMap dla Polski jest już zainstalowany i **przetestowany** na danych testowych.

## 📥 Kroki do wykonania lokalnie

### 1️⃣ Pobierz dane OSM Polski

```bash
# Clone repozytorium
git clone https://github.com/baW01/Navi.git
cd Navi

# Pobierz dane OSM dla Polski (~300 MB)
python download_poland_osm.py
```

**Alternatywnie (ręcznie):**
- Przejdź do: https://download.geofabrik.de/europe/poland.html
- Pobierz: `poland-latest.osm.pbf` (~300 MB)
- Umieść w: `data/poland/poland-latest.osm.pbf`

### 2️⃣ Uruchom pipeline przetwarzania

```bash
# Option A: Automatycznie (skrypt bash)
bash process_poland_osm.sh

# Option B: Ręcznie - krok po kroku
source .venv/bin/activate
pip install -e .

# Importuj OSM -> canonical schema
navi import-osm data/poland/poland-latest.osm.pbf --out data/poland/intermediate

# Zbuduj graf routingu
navi build-graph --input data/poland/intermediate --out data/poland/graph

# Eksportuj do formatu NDS-like (otwarty JSON)
navi export-nds-like --input data/poland/intermediate --out data/poland/nds_like

# Eksportuj do formatu NDS.Live PoC (warstwowy)
navi export-nds-live-poc --input data/poland/intermediate --out data/poland/nds_live_poc

# Waliduj dane
navi validate --input data/poland/intermediate
```

## 📊 Struktura wyjściowych danych

Po przetworzeniu otrzymasz:

```
data/poland/
├── intermediate/
│   └── canonical.json          # Kanoniczna reprezentacja (całe dane)
├── graph/
│   └── graph.json              # Graf routingu (węzły + krawędzie)
├── nds_like/                   # Format otwarty (7 plików JSON)
│   ├── road_network.json       # Drogi
│   ├── junctions.json          # Skrzyżowania
│   ├── turn_restrictions.json  # Ograniczenia skrętów
│   ├── addresses.json          # Adresy
│   ├── poi.json                # Punkty zainteresowania
│   ├── metadata.json
│   └── manifest.json
└── nds_live_poc/               # Format warstwowy
    ├── layers/
    │   ├── road_network/       # Warstwy drogi
    │   ├── topology/           # Topologia
    │   ├── addressing/         # Adresy
    │   ├── poi/                # POI
    │   └── restrictions/       # Ograniczenia
    └── manifest.json
```

## 🔍 Przykładowe dane (już gotowe)

Możesz obejrzeć rezultaty na danych testowych:

```bash
# Struktura
tree data/test

# Canonical schema
python -m json.tool data/test/intermediate/canonical.json | less

# NDS-like road network
python -m json.tool data/test/nds_like/road_network.json | less

# Junctions (skrzyżowania)
python -m json.tool data/test/nds_like/junctions.json | less

# Turn restrictions (ograniczenia skrętów)
python -m json.tool data/test/nds_like/turn_restrictions.json | less
```

## ⏱️ Czas przetwarzania

- **Dane testowe** (mini.osm): ~1 sekunda
- **Polska pełna** (poland-latest.osm.pbf): ~5-15 minut (zależy od CPU)

## 🎯 Zawartość danych

### road_network.json (każdy segment drogi)
```json
{
  "id": "segment_id",
  "from_junction_id": "node_1",
  "to_junction_id": "node_2",
  "geometry": [[lon, lat], ...],
  "name": "Nazwa drogi",
  "ref": "referencja OSM",
  "road_class": "primary|secondary|tertiary|...",
  "oneway": true/false,
  "maxspeed": 50,          // km/h
  "lanes": 2,
  "surface": "asphalt|concrete|gravel|...",
  "access_car": true,
  "toll": false,
  "bridge": false,
  "tunnel": false
}
```

### junctions.json (skrzyżowania)
```json
{
  "id": "junction_id",
  "lat": 52.0,
  "lon": 21.0,
  "connected_segment_ids": ["seg_id1", "seg_id2", ...]
}
```

### turn_restrictions.json
```json
{
  "id": "restriction_id",
  "type": "no_left_turn|no_right_turn|no_u_turn|only_left_turn|...",
  "from_segment_id": "seg_1",
  "to_segment_id": "seg_2",
  "via_junction_id": "node_id"
}
```

## 🚀 Dalsze możliwości

Po przetworzeniu danych możesz:

1. **Routing** - obliczyć trasy między punktami
   ```bash
   navi route --from 52.0,21.0 --to 52.1,21.1 --graph data/poland/graph
   ```

2. **Eksport GeoJSON** - wizualizacja w mapach
   ```bash
   # GeoJSON drogi są automatycznie generowane w NDS-like/NDS.Live
   ```

3. **Walidacja** - sprawdzenie integralności danych
   ```bash
   navi validate --input data/poland/intermediate
   ```

## 📝 Uwagi

- Pipeline obsługuje formaty `.osm` i `.pbf`
- Dane są w EPSG:4326 (WGS84) - standardowy format geograficzny
- Wszystko jest opensource i nie wymaga żadnych API
- Całe przetwarzanie odbywa się lokalnie

---

**Pytania?** Sprawdź dokumentację w `docs/` lub uruchom `navi --help`
