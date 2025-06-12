#!/usr/bin/env python3
import os
import sys

# Añadir la carpeta scrapers al path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRAPERS_PATH = os.path.join(CURRENT_DIR, "scrapers")
sys.path.insert(0, SCRAPERS_PATH)

from scraper_dia import scrape_dia

if __name__ == "__main__":
    print("Iniciando actualización diaria...")
    scrape_dia()
    print("Actualización completada.")
