import requests
from bs4 import BeautifulSoup
from supabase import create_client
import re
import time
import config

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

    url = "https://tienda.dia.es/api/categories/"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    print(f"🔍 Estado respuesta: {r.status_code}")
    if r.status_code != 200:
        print(f"⚠️ Error al obtener categorías de DIA: {r.text}")
        return

    categorias = r.json()
    print(f"📦 Categorías encontradas: {len(categorias)}")

    for cat in categorias:
        if "id" in cat:
            print(f"🔍 Procesando categoría: {cat['name']}")
            url = f"https://tienda.dia.es/api/categories/{cat['id']}/products/"
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                productos = r.json()
                print(f"📦 Productos encontrados en {cat['name']}: {len(productos)}")
                for p in productos:
                    try:
                        nombre = p["name"]
                        precio = float(p["price"])
                        cantidad = 1.0
                        unidad = "ud"
                        id_producto = get_or_create_producto(nombre, cantidad, unidad)
                        upsert_supermercado_producto(id_super, id_producto, precio)
                        print(f"✅ Insertado {nombre} - {precio}€")
                        time.sleep(0.1)
                    except Exception as e:
                        print(f"⚠️ Error en producto: {e}")
            else:
                print(f"⚠️ Error al obtener productos de {cat['name']}: {r.text}")

def scrape_and_upsert():
    scrap_dia()

if __name__ == "__main__":
    scrape_and_upsert()
