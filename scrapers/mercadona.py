import time
import requests
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9",
}

def safe_get(url, retries=3, backoff=2):
    for i in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.raise_for_status()
            return r
        except Exception as e:
            print(f"[Mercadona] Intento {i+1} fallido: {e}")
            time.sleep(backoff * (i+1))
    raise Exception("[Mercadona] No se pudo conectar tras varios intentos")

def scrape_mercadona():
    url = "https://www.mercadona.es/es/ofertas"
    r = safe_get(url)
    data = r.json() if r.headers.get("content-type", "").startswith("application/json") else None
    if data is None:
        # Intentar obtener productos por otro método (por ejemplo parsear html o API)
        raise Exception("No se pudo obtener JSON de Mercadona")
    productos = []
    for item in data.get("products", []):
        nombre = item.get("name")
        precio = item.get("price", {}).get("offerPrice")
        cantidad = 1.0
        unidad = "ud"
        if nombre and precio is not None:
            productos.append((nombre, precio, cantidad, unidad))
    return productos

def get_or_create_supermercado(supabase, nombre):
    res = supabase.table("supermercado").select("id_supermercado").eq("nombre", nombre).execute()
    if res.data:
        return res.data[0]["id_supermercado"]
    else:
        res = supabase.table("supermercado").insert({"nombre": nombre}).select("id_supermercado").execute()
        return res.data[0]["id_supermercado"]

def scrape_and_upsert():
    print("📦 Iniciando scrapeo de productos Mercadona")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    id_supermercado = get_or_create_supermercado(supabase, "Mercadona")
    productos = scrape_mercadona()

    for nombre, precio, cantidad, unidad in productos:
        # Check producto
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

        # Upsert precio
        supabase.table("supermercadoproducto").upsert({
            "id_supermercado": id_supermercado,
            "id_producto": id_producto,
            "precio_unitario": precio
        }).execute()
    print("✅ Mercadona actualizado")
