# updater.py
from scrapers import (
    mercadona, dia, carrefour, lidl, aldi, eroski,
    hipercor, alcampo, eljamon, ahorramas
)

def main():
    for module in [mercadona, dia, carrefour, lidl, aldi, eroski,
                   hipercor, alcampo, eljamon, ahorramas]:
        try:
            module.scrape_and_upsert()
            print(f"[OK] {module.__name__}")
        except Exception as e:
            print(f"[ERROR] {module.__name__}: {e}")

if __name__ == "__main__":
    main()
