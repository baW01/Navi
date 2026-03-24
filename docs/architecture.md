# Architektura

Pipeline jest podzielony na warstwy:

1. `ingest` – odczyt OSM (`.pbf` przez `pyosmium`, `.osm` XML fallback).
2. `normalize` – konwersja do jawnego canonical schema niezależnego od OSM/NDS.
3. `routing` – budowa skierowanego grafu z wagami (`length_m`, `travel_time_s`) i demo trasy.
4. `exporters` – eksport do `nds_like` i `nds_live_poc`.
5. `validators` – kontrola jakości danych i topologii.
6. `cli` – komendy uruchamiające cały proces.

## Artefakty pipeline

- `canonical.json` – canonical schema po imporcie i normalizacji.
- `graph.json` – snapshot grafu routingu.
- `validation_report.json` – raport walidacji.
- katalogi eksportowe `nds_like` i `nds_live_poc`.

## Compliance

Projekt nie implementuje obchodzenia zabezpieczeń OEM ani zamkniętych binarnych formatów. `nds_live_poc` jest opisanym PoC koncepcyjnym.
