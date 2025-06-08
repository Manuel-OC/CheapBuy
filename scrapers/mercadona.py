from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def get_or_create_supermercado(supabase, nombre):
    res = supabase.table("supermercado").select("id_supermercado").eq("nombre", nombre).execute()
    if res.data:
        return res.data[0]["id_supermercado"]
    else:
        res = supabase.table("supermercado").insert({"nombre": nombre}).select("id_supermercado").execute()
        return res.data[0]["id_supermercado"]

def scrape_and_upsert():
    print("📦 Iniciando scrapeo de productos Mercadona (Selenium)")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    id_supermercado = get_or_create_supermercado(supabase, "Mercadona")

    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    driver.get("https://www.mercadona.es/es/ofertas")
    time.sleep(5)  # Esperar que cargue JS y productos

    productos = []
    cards = driver.find_elements(By.CSS_SELECTOR, "li.product-list__item")
    for c in cards:
        try:
            nombre = c.find_element(By.CSS_SELECTOR, "span.product-title").text.strip()
            precio_str = c.find_element(By.CSS_SELECTOR, "span.price__value").text.strip().replace(",", ".")
            precio = float(precio_str)
            cantidad = 1.0
            unidad = "ud"
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

    print("✅ Mercadona actualizado")
