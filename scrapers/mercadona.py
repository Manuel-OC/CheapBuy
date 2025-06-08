# scrapers/mercadona.py
import requests
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def scrape_and_upsert():
    sname = "Mercadona"
    url = "https://tienda.mercadona.es/api/categories/"
    r = requests.get(url)
    data = r.json()
    sid = supabase.table("supermercado").upsert({"nombre": sname}, on_conflict="nombre").execute().data[0]["id_supermercado"]
    for cat in data:
        for sub in cat.get("categories", []):
            for prod in sub.get("products", []):
                nombre = prod["display_name"]
                cantidad = float(prod.get("size", "1").split()[0])
                unidad = prod.get("unit_size", "")
                precio = float(prod["price_instructions"]["price"])
                # Upsert product
                p = supabase.table("producto").select("id_producto") \
                    .eq("nombre", nombre).execute().data
                if p:
                    pid = p[0]["id_producto"]
                else:
                    pid = supabase.table("producto").insert({"nombre": nombre, "cantidad": cantidad, "unidad": unidad}).execute().data[0]["id_producto"]
                # Upsert precio
                supabase.table("supermercadoproducto").upsert({
                    "id_supermercado": sid, "id_producto": pid, "precio_unitario": precio
                }, on_conflict=["id_supermercado","id_producto"]).execute()
