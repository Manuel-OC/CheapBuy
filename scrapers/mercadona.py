# scrapers/mercadona.py

import requests
import time
import sys
import os
import traceback
from supabase import create_client

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

def get_or_create_supermercado(nombre):
    res = supabase.table("supermercado").select("id_supermercado").eq("nombre", nombre).execute()
    if res.data:
        return res.data[0]["id_supermercado"]
    ins = supabase.table("supermercado").insert({"nombre": nombre}).execute()
    if ins.data:
        return ins.data[0]["id_supermercado"]
    raise Exception(f"Error insertando supermercado {nombre}")

def get_or_create_producto(nombre, cantidad, unidad):
    res = supabase.table("producto").select("id_producto").eq("nombre", nombre).eq("cantidad", cantidad).eq("unidad", unidad).execute()
    if res.data:
        return res.data[0]["id_producto"]
    ins = supabase.table("producto").insert({"nombre": nombre, "cantidad": cantidad, "unidad": unidad}).execute()
    if ins.data:
        return ins.data[0]["id_producto"]
    raise Exception(f"Error insertando producto {nombre}")

def upsert_supermercado_producto(id_supermercado, id_producto, precio_unitario):
    del_res = supabase.table("supermercadoproducto").delete().eq("id_supermercado", id_supermercado).eq("id_producto", id_producto).execute()
    if del_res.error:
        print(f"Advertencia: error al borrar antes de upsert: {del_res.error}")
    ins_res = supabase.table("supermercadoproducto").insert({
        "id_supermercado": id_supermercado,
        "id_producto": id_producto,
        "precio_unitario": precio_unitario
    }).execute()
    if ins_res.error:
        raise Exception(f"Error insertando relación supermercado-producto: {ins_res.error}")

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

    categorias = requests.get(url, headers=headers).json()
    for cat in categorias:
        if "categories" not in cat:
            continue
        for subcat in cat["categories"]:
            products = subcat.get("products", [])
            for product in products:
                try:
                    nombre = product["display_name"]
                    precio = float(product["price_instructions"]["unit_price"])
                    cantidad, unidad = parse_cantidad_unidad(nombre)
                    print(f"Procesando: {nombre} | Cantidad: {cantidad} {unidad} | Precio: {precio}")
                    id_producto = get_or_create_producto(nombre, cantidad, unidad)
                    upsert_supermercado_producto(id_super, id_producto, precio)
                    print(f"✅ Insertado {nombre} - {precio}€")
                    time.sleep(0.1)
                except Exception:
                    print(f"⚠️ Error en producto {product.get('display_name', 'desconocido')}:")
                    traceback.print_exc()

def scrape_and_upsert():
    scrap_mercadona()

if __name__ == "__main__":
    scrap_mercadona()

