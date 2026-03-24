#!/usr/bin/env python3
"""
Skrypt do pobrania danych OSM dla Polski z Geofabrika.
Uruchom: python download_poland_osm.py
"""

import os
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError
import sys

def download_poland_osm():
    """Pobiera plik OSM dla Polski."""
    url = "https://download.geofabrik.de/europe/poland-latest.osm.pbf"
    output_dir = Path("data/poland")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "poland-latest.osm.pbf"
    
    print(f"📥 Pobieranie danych OSM dla Polski...")
    print(f"   URL: {url}")
    print(f"   Rozmiar: ~300 MB")
    print(f"   Do: {output_file}")
    print()
    
    try:
        with urlopen(url) as response:
            total_size = int(response.headers.get('Content-Length', 0))
            block_size = 8192
            downloaded = 0
            
            with open(output_file, 'wb') as f:
                while True:
                    buffer = response.read(block_size)
                    if not buffer:
                        break
                    f.write(buffer)
                    downloaded += len(buffer)
                    
                    # Postęp
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        mb = downloaded / (1024*1024)
                        total_mb = total_size / (1024*1024)
                        print(f"\r   ⏳ {percent:.1f}% ({mb:.1f} MB / {total_mb:.1f} MB)", end='', flush=True)
            
            print(f"\n✅ Pobieranie ukończone: {output_file}")
            print(f"   Rozmiar: {os.path.getsize(output_file) / (1024*1024):.1f} MB")
            
    except URLError as e:
        print(f"❌ Błąd pobierania: {e}")
        print(f"   Spróbuj ściągnąć ręcznie z: {url}")
        sys.exit(1)

if __name__ == "__main__":
    download_poland_osm()
