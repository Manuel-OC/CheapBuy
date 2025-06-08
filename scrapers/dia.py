import requests
from bs4 import BeautifulSoup
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def scrape_and_upsert():
    sname = "Dia"
    sid = supabase.table("supermercado").upsert(
        {"nombre": sname},
        on_conflict="nombre"
    ).execute().data[0]["id_supermercado"]

    base_url = "https://www.dia.es/compra-online/browse/"
    categorias = ["lacteos", "panaderia", "huevos-y-helados"]  # puedes ampliar

    for cat in categorias:
        page = 1
        while True:
            url = f"{base_url}{cat}/?page={page}"
            r = requests.get(url)
            soup = BeautifulSoup(r.text, "html.parser")
            cards = soup.select(".product-tile")

            if not cards:
                break

            for c in cards:
                nombre = c.select_one(".title").text.strip()
                precio = c.select_one(".price__offer").text.strip().replace("€", "").replace(",", ".")
                cantidad = 1.0
                unidad = "ud"

                upsert_product(nombre, cantidad, unidad, precio, sid)
            page += 1

    print(f"[OK] DIA completado")

def upsert_product(nombre, cantidad, unidad, precio, sid):
    # Buscar o insertar producto
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
