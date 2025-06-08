import requests
from bs4 import BeautifulSoup
from supabase import create_client
import re
import time
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

def scrap_dia():
    nombre_super = "DIA"
    id_super = get_or_create_supermercado(nombre_super)

    url = "https://www.dia.es/compra-online/supermercado/"
    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers)
    print(f"🌐 Estado respuesta: {r.status_code}")
    print(r.text[:500])  # para ver si es HTML real o vacío

    soup = BeautifulSoup(r.text, "html.parser")
    productos = soup.select(".product-tile")
    print(f"🔍 Productos encontrados: {len(productos)}")

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
            print(f"✅ {nombre} - {precio}€")
            time.sleep(0.2)
        except Exception as e:
            print(f"⚠️ Error producto DIA: {e}")

def scrape_and_upsert():
    scrap_dia()

if __name__ == "__main__":
    scrap_dia()
