#!/bin/bash
# Kompletny pipeline przetwarzania OSM dla Polski
# Użycie: ./process_poland_osm.sh
# LUB dla testowych danych: ./process_poland_osm.sh --test

set -e  # Wyjdź na błędzie

VENV=".venv"
DATA_DIR="data/poland"
TEST_MODE=false

# Parsowanie argumentów
if [ "$1" == "--test" ]; then
    TEST_MODE=true
    echo "🧪 TRYB TESTOWY - używam mini.osm"
fi

# 1. Aktywacja środowiska
echo "📦 Aktywowanie virtual environment..."
if [ ! -d "$VENV" ]; then
    python -m venv "$VENV"
fi
source "$VENV/bin/activate"

# 2. Instalacja zależności
echo "📥 Instalowanie Navi..."
pip install -e . -q

# 3. Przygotowanie danych
if [ "$TEST_MODE" = true ]; then
    echo "📂 Konfiguracja trybu testowego..."
    OSM_FILE="tests/fixtures/mini.osm"
    DATA_DIR="data/test"
else
    echo "📂 Konfiguracja dla pełnych danych Polski..."
    mkdir -p "$DATA_DIR"
    OSM_FILE="$DATA_DIR/poland-latest.osm.pbf"
    
    if [ ! -f "$OSM_FILE" ]; then
        echo "❌ Plik $OSM_FILE nie znaleziony!"
        echo "   Pobierz go za pomocą: python download_poland_osm.py"
        exit 1
    fi
fi

echo "✅ Pliki: $OSM_FILE"
echo ""

# 4. Import OSM -> canonical schema
echo "🔄 Krok 1/4: Importowanie OSM do canonical schema..."
navi import-osm "$OSM_FILE" --out "$DATA_DIR/intermediate" --verbose

# 5. Budowanie grafu routingu
echo ""
echo "🔄 Krok 2/4: Budowanie grafu routingu..."
navi build-graph --input "$DATA_DIR/intermediate" --out "$DATA_DIR/graph"

# 6. Eksport do nds_like
echo ""
echo "🔄 Krok 3/4: Eksport do nds_like (otwarty JSON)..."
navi export-nds-like --input "$DATA_DIR/intermediate" --out "$DATA_DIR/nds_like"

# 7. Eksport do nds_live_poc
echo ""
echo "🔄 Krok 4/4: Eksport do nds_live_poc (warstwowy)..."
navi export-nds-live-poc --input "$DATA_DIR/intermediate" --out "$DATA_DIR/nds_live_poc"

# 8. Walidacja
echo ""
echo "✅ Walidacja datasets..."
navi validate --input "$DATA_DIR/intermediate"

# 9. Podsumowanie
echo ""
echo "════════════════════════════════════════════════"
echo "✨ PRZETWARZANIE UKOŃCZONE!"
echo "════════════════════════════════════════════════"
echo ""
echo "📊 Wyniki w:"
echo "   🗂️  $DATA_DIR/intermediate/     → canonical schema"
echo "   📈 $DATA_DIR/graph/             → graf routingu"
echo "   🗺️  $DATA_DIR/nds_like/         → format NDS-like"
echo "   🌐 $DATA_DIR/nds_live_poc/      → format NDS.Live PoC"
echo ""
echo "🔍 Zawartość plików:"
ls -lh "$DATA_DIR"/*/ 2>/dev/null | awk '{print "     " $9 " (" $5 ")"}'
echo ""
