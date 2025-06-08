import re
import requests
from bs4 import BeautifulSoup
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9",
}

def parse_cantidad_unidad(nombre_producto):
    match = re.search(r"(\d+(?:[.,]\d+)?)\s?(kg|g|l|ml|ud|unidad|unidad/es)?", nombre_producto, re.I)
    if match:
        cantidad = match.group(1).replace(',', '.')
        unidad = match.group(2)
        if unidad:
            unidad = unidad.lower()
            if unidad == 'g':
                cantidad = float(cantidad) / 1000
                unidad = 'kg'
            elif unidad == 'ml':
                cantidad = float(cantidad) / 1000
                unidad = 'l'
            elif unidad in ['ud', 'unidad', 'unidad/es']:
                unidad = 'ud'
        else:
            unidad = 'ud'
        return float(cantidad), unidad
    return 1.0, 'ud'

def scrape_carrefour():
    url = "https://www.carrefour.es/supermercado/"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    productos_html = soup.select("div.product-card")
    productos = []
    for p in productos_html:
        nombre_tag = p.select_one("div.product-card__name")
        precio_tag = p.select_one("div.product-card__price")

        if nombre_tag and precio_tag:
            nombre = nombre_tag.get_text(strip=True)
            precio_str = precio_tag.get_text(strip=True).replace('€', '').replace(',', '.').strip()
            try:
                precio = float(precio_str)
                productos.append((nombre, precio))
            except:
                continue
    return productos

def get_or_create_supermercado(supabase, nombre):
    res = supabase.table("supermercado").select("id_supermercado").eq("nombre", nombre).execute()
    if res.data:
        return res.data[0]["id_supermercado"]
    else:
        res = supabase.table("supermercado").insert({"nombre": nombre}).select("id_supermercado").execute()
        return res.data[0]["id_supermercado"]

def scrape_and_upsert():
    print("📦 Iniciando scrapeo de productos Carrefour")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    id_supermercado = get_or_create_supermercado(supabase, "Carrefour")
    productos = scrape_carrefour()

    for nombre, precio in productos:
        cantidad, unidad = parse_cantidad_unidad(nombre)

        res = supabase.table("producto").select("id_producto")\
            .eq("nombre", nombre).eq("cantidad", cantidad).eq("unidad", unidad).execute()
        if res.data:
            id_producto = res.data[0]["id_producto"]
        else:
            res = supabase.table("producto").insert({
                "nombre": nombre,
                "cantidad": cantidad,
                "unidad": unidad
            }).select("id_producto").execute()
            id_producto = res.data[0]["id_producto"]

        supabase.table("supermercadoproducto").upsert({
            "id_supermercado": id_supermercado,
            "id_producto": id_producto,
            "precio_unitario": precio
        }).execute()
    print("✅ Carrefour actualizado")
