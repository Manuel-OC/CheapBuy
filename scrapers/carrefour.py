# scrapers/carrefour.py

import requests
from bs4 import BeautifulSoup
from supabase import create_client
import re
import time
import traceback
import sys
import os

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
    cantidad = 1.0
    unidad = "ud"
    match = re.search(r"(\d+[\.,]?\d*)\s*(kg|g|l|ml|ud|unidad|u)", nombre, re.I)
    if match:
        cantidad = float(match.group(1).replace(",", "."))
        unidad = match.group(2).lower()
        if unidad == "g":
            cantidad /= 1000
            unidad = "kg"
        elif unidad == "ml":
            cantidad /= 1000
            unidad = "l"
    return cantidad, unidad

def scrap_carrefour():
    print("📦 Iniciando scrapeo de productos Carrefour")
    id_super = get_or_create_supermercado("Carrefour")
    url = "https://www.carrefour.es/supermercado/"
    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    productos = soup.select(".product-list-item")  # Selector a revisar si cambia

    for p in productos:
        try:
            nombre = p.select_one(".product-title").text.strip()
            precio_text = p.select_one(".product-price").text.strip().replace("€", "").replace(",", ".")
            precio = float(precio_text)

            cantidad, unidad = parse_cantidad_unidad(nombre)
            print(f"Procesando: {nombre} | Cantidad: {cantidad} {unidad} | Precio: {precio}")

            id_producto = get_or_create_producto(nombre, cantidad, unidad)
            upsert_supermercado_producto(id_super, id_producto, precio)
            print(f"✅ Insertado {nombre} - {precio}€")
            time.sleep(0.2)
        except Exception:
            print(f"⚠️ Error producto Carrefour:")
            traceback.print_exc()

def scrape_and_upsert():
    scrap_carrefour()

if __name__ == "__main__":
    scrap_carrefour()
