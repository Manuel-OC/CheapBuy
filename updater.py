import os
from dia_scraper import scrape_dia
from supabase import create_client

def main():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    print(f"Supabase URL: {supabase_url}")
    if not supabase_url or not supabase_key:
        print("❌ ERROR: Supabase credentials not found.")
        return

    supabase = create_client(supabase_url, supabase_key)
    data = scrape_dia()

    print(f"Scraped {len(data)} products")

    for product in data:
        print(f"Inserting: {product}")
        try:
            response = supabase.table("precios_dia").insert(product).execute()
            print(f"✅ Inserted: {response}")
        except Exception as e:
            print(f"❌ Failed to insert: {e}")
