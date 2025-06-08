import requests
import time
import sys
import os
from supabase import create_client

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

def get_or_create_supermercado(nombre):
    res = supabase.table("supermercado").select("id_supermercado").eq("nombre", nombre).execute()
    print("🔍 get_or_create_supermercado:", res.data)
    if res.data:
        return res.data[0]["id_supermercado"]
    ins = supabase.table("supermercado").insert({"nombre": nombre}).execute()
    print("🆕 insert supermercado:", ins.data, ins.error)
    return ins.data[0]["id_supermercado"]

def get_or_create_producto(nombre, cantidad, unidad):
    res = supabase.table("producto").select("id_producto").eq("nombre", nombre).eq("cantidad", cantidad).eq("unidad", unidad).execute()
    if res.data:
        return res.data[0]["id_producto"]
    ins = supabase.table("producto").insert({"nombre": nombre, "cantidad": cantidad, "unidad": unidad}).execute()
    print("🆕 insert producto:", ins.data, ins.error)
    return ins.data[0]["id_producto"]

def upsert_supermercado_producto(id_supermercado, id_producto, precio_unitario):
    supabase.table("supermercadoproducto").delete().eq("id_supermercado", id_supermercado).eq("id_producto", id_producto).execute()
    ins = supabase.table("supermercadoproducto").insert({
        "id_supermercado": id_supermercado,
        "id_producto": id_producto,
        "precio_unitario": precio_unitario
    }).execute()
    print("🆕 insert supermercadoproducto:", ins.data, ins.error)

def parse_cantidad_unidad(nombre):
    import re
    cantidad = 1.0
    unidad = "ud"
    match = re.search(r"(\d+(?:[.,]\d+)?)(\s*)(kg|g|l|ml|ud|u|unidad)", nombre.lower())
    if match:
        cantidad = float(match.group(1).replace(",", "."))
        unidad = match.group(3)
        if unidad == "g":
            cantidad /= 1000
            unidad = "kg"
        elif unidad == "ml":
            cantidad /= 1000
            unidad = "l"
    return cantidad, unidad

def scrap_mercadona():
    print("📦 Iniciando scrapeo de productos Mercadona")
    id_super = get_or_create_supermercado("Mercadona")
    url = "https://tienda.mercadona.es/api/categories/"
    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers)
    print(f"🌐 Estado respuesta: {r.status_code}")
    categorias = r.json()

    for cat in categorias:
        if "categories" not in cat:
            continue
        for subcat in cat["categories"]:
            products = subcat.get("products", [])
            print(f"📁 Subcategoría '{subcat.get('name')}' - productos encontrados: {len(products)}")
            for product in products:
                try:
                    nombre = product["display_name"]
                    precio = float(product["price_instructions"]["unit_price"])
                    cantidad, unidad = parse_cantidad_unidad(nombre)
                    id_producto = get_or_create_producto(nombre, cantidad, unidad)
                    upsert_supermercado_producto(id_super, id_producto, precio)
                    print(f"✅ {nombre} - {precio}€")
                    time.sleep(0.1)
                except Exception as e:
                    print(f"⚠️ Error en producto: {e}")

def scrape_and_upsert():
    scrap_mercadona()

if __name__ == "__main__":
    scrap_mercadona()
