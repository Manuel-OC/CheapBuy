from scrapers import mercadona, dia, carrefour

def main():
    for module in [mercadona, dia, carrefour]:
        try:
            module.scrape_and_upsert()
            print(f"[OK] {module.__name__}")
        except Exception as e:
            print(f"[ERROR] {module.__name__}: {e}")

if __name__ == "__main__":
    main()
