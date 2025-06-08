import requests
from bs4 import BeautifulSoup
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def scrape_and_upsert():
    sname = "Carrefour"
    sid = supabase.table("supermercado").upsert(
        {"nombre": sname},
        on_conflict="nombre"
    ).execute().data[0]["id_supermercado"]

    base_url = "https://www.carrefour.es/supermercado/search"
    queries = ["leche", "pan", "huevos"]  # añade más categorías

    for q in queries:
        params = {"q": q}
        r = requests.get(base_url, params=params)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.select(".product-card")

        for c in items:
            nombre = c.select_one(".product-card__title").text.strip()
            precio = c.select_one(".product-card__price").text.strip().replace("€", "").replace(",", ".")
            cantidad = 1.0
            unidad = "ud"

            upsert_product(nombre, cantidad, unidad, precio, sid)

    print(f"[OK] Carrefour completado")

def upsert_product(nombre, cantidad, unidad, precio, sid):
    res = supabase.table("producto").select("id_producto").eq("nombre", nombre).execute().data
    if res:
        pid = res[0]["id_producto"]
    else:
        pid = supabase.table("producto").insert({
            "nombre": nombre,
            "cantidad": cantidad,
            "unidad": unidad
        }).execute().data[0]["id_producto"]

    supabase.table("supermercadoproducto").upsert({
        "id_supermercado": sid,
        "id_producto": pid,
        "precio_unitario": float(precio)
    }, on_conflict=["id_supermercado", "id_producto"]).execute()
