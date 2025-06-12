#!/usr/bin/env python3
import os
from scrapers.scraper_dia import scrape_dia      # Import corregido

def main():
    print("▶️ Iniciando updater.py")

    data = scrape_dia()
    print(f"📝 Productos encontrados: {len(data)}")
    for item in data[:5]:  # mostramos los primeros 5 como prueba
        print(" -", item)

if __name__ == "__main__":
    main()
