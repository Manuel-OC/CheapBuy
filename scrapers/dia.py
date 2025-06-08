import requests
from bs4 import BeautifulSoup
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

def get_or_create_supermercado(supabase):
    data = [{"nombre": "Dia"}]
    res = supabase.table("supermercado").upsert(data, on_conflict="nombre").execute()
    if res.data:
        return res.data[0]["id_supermercado"]
    raise Exception("No se pudo crear o obtener Dia")

def scrape_and_upsert():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    id_supermercado = get_or_create_supermercado(supabase)

    url = "https://www.dia.es/compra-online"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise Exception(f"Error accediendo a DIA: {r.status_code}")

    soup = BeautifulSoup(r.text, "lxml")

    productos = []
    items = soup.select("div.product-item")  # Ajusta selector según web

    for item in items:
        try:
            nombre = item.select_one("h3.product-title").text.strip()
            precio_text = item.select_one("span.price").text.strip().replace("€", "").replace(",", ".")
            precio = float(precio_text)
            cantidad_text = item.select_one("span.quantity").text.strip()
            cantidad, unidad = cantidad_text.split(" ", 1)
            cantidad = float(cantidad.replace(",", "."))
            productos.append({
                "nombre": nombre,
                "cantidad": cantidad,
                "unidad": unidad,
                "precio_unitario": precio
            })
        except Exception:
            continue

    for prod in productos:
        res_prod = supabase.table("producto").upsert(
            [{"nombre": prod["nombre"], "cantidad": prod["cantidad"], "unidad": prod["unidad"]}],
            on_conflict="nombre"
        ).execute()
        if not res_prod.data:
            continue
        id_producto = res_prod.data[0]["id_producto"]

        supabase.table("supermercadoproducto").upsert(
            [{
                "id_supermercado": id_supermercado,
                "id_producto": id_producto,
                "precio_unitario": prod["precio_unitario"]
            }],
            on_conflict=["id_supermercado", "id_producto"]
        ).execute()
