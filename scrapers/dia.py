import requests
from bs4 import BeautifulSoup
from supabase import create_client
import re
import time
import config  # <-- importas tu archivo config.py

SUPABASE_URL = config.SUPABASE_URL
SUPABASE_KEY = config.SUPABASE_KEY
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_or_create_supermercado(nombre):
    res = supabase.table("supermercado").select("id_supermercado").eq("nombre", nombre).execute()
    if res.data:
        return res.data[0]["id_supermercado"]
    ins = supabase.table("supermercado").insert({"nombre": nombre}).execute()
    return ins.data[0]["id_supermercado"]

def get_or_create_producto(nombre, cantidad, unidad):
    res = supabase.table("producto").select("id_producto").eq("nombre", nombre).eq("cantidad", cantidad).eq("unidad", unidad).execute()
    if res.data:
        return res.data[0]["id_producto"]
    ins = supabase.table("producto").insert({"nombre": nombre, "cantidad": cantidad, "unidad": unidad}).execute()
    return ins.data[0]["id_producto"]

def upsert_supermercado_producto(id_supermercado, id_producto, precio_unitario):
    supabase.table("supermercadoproducto").delete().eq("id_supermercado", id_supermercado).eq("id_producto", id_producto).execute()
    supabase.table("supermercadoproducto").insert({
        "id_supermercado": id_supermercado,
        "id_producto": id_producto,
        "precio_unitario": precio_unitario
    }).execute()

def scrap_dia():
    nombre_super = "DIA"
    id_super = get_or_create_supermercado(nombre_super)

    url = "https://www.dia.es/compra-online/supermercado/"

    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    productos = soup.select(".product-tile")

    for p in productos:
        try:
            nombre = p.select_one(".product-name").text.strip()
            precio_text = p.select_one(".price").text.strip().replace("€", "").replace(",", ".")
            precio = float(precio_text)

            cantidad = 1.0
            unidad = "ud"
            match = re.search(r"(\d+[\.,]?\d*)\s*(kg|g|l|ml|ud|unidad|u)", nombre, re.I)
            if match:
                cantidad = float(match.group(1).replace(",", "."))
                unidad = match.group(2).lower()
                if unidad == "g":
                    cantidad /= 1000
                    unidad = "kg"
                if unidad == "ml":
                    cantidad /= 1000
                    unidad = "l"

            id_producto = get_or_create_producto(nombre, cantidad, unidad)
            upsert_supermercado_producto(id_super, id_producto, precio)
            print(f"Insertado {nombre} - {precio}€")
            time.sleep(0.2)
        except Exception as e:
            print(f"Error producto DIA: {e}")

def scrape_and_upsert():
    scrap_dia()

if __name__ == "__main__":
    scrap_dia()
