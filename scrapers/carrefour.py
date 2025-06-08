from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import re

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

def get_or_create_supermercado(supabase, nombre):
    res = supabase.table("supermercado").select("id_supermercado").eq("nombre", nombre).execute()
    if res.data:
        return res.data[0]["id_supermercado"]
    else:
        res = supabase.table("supermercado").insert({"nombre": nombre}).select("id_supermercado").execute()
        return res.data[0]["id_supermercado"]

def scrape_and_upsert():
    print("📦 Iniciando scrapeo de productos Carrefour (Selenium)")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    id_supermercado = get_or_create_supermercado(supabase, "Carrefour")

    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    driver.get("https://www.carrefour.es/supermercado/")
    time.sleep(5)

    productos = []
    cards = driver.find_elements(By.CSS_SELECTOR, "article.product")
    for c in cards:
        try:
            nombre = c.find_element(By.CSS_SELECTOR, "h3.product-title").text.strip()
            precio_str = c.find_element(By.CSS_SELECTOR, "span.price-integer").text.strip()
            decimales = c.find_element(By.CSS_SELECTOR, "span.price-decimals").text.strip()
            precio = float(precio_str + "." + decimales)
            cantidad, unidad = parse_cantidad_unidad(nombre)
            productos.append((nombre, precio, cantidad, unidad))
        except Exception as e:
            continue

    driver.quit()

    for nombre, precio, cantidad, unidad in productos:
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
