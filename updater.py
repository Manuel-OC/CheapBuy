#!/usr/bin/env python3
import os
import sys

# 👉 Añadir la ruta actual al sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "scrapers"))

from scraper_dia import scrape_dia  # Sin el prefijo "scrapers."

def main():
    print("▶️ Iniciando updater.py")

    data = scrape_dia()
    print(f"📝 Productos encontrados: {len(data)}")
    for item in data[:5]:  # mostramos los primeros 5 como prueba
        print(" -", item)

if __name__ == "__main__":
    main()
