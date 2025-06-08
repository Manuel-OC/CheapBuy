import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    # No usar --user-data-dir
    driver = webdriver.Chrome(options=options)
    return driver

def get_or_create_supermercado(supabase):
    data = [{"nombre": "Carrefour"}]
    res = supabase.table("supermercado").upsert(data, on_conflict="nombre").execute()
    if res.data:
        return res.data[0]["id_supermercado"]
    raise Exception("No se pudo crear o obtener Carrefour")

def scrape_and_upsert():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    id_supermercado = get_or_create_supermercado(supabase)

    driver = get_driver()
    try:
        driver.get("https://www.carrefour.es/supermercado/")
        time.sleep(5)  # Esperar carga JS

        productos = []
        cards = driver.find_elements_by_css_selector("div.product-tile")  # Ajustar selector
        for card in cards:
            try:
                nombre = card.find_element_by_css_selector("h3.product-name").text.strip()
                precio_text = card.find_element_by_css_selector("span.price").text.strip().replace("€", "").replace(",", ".")
                precio = float(precio_text)
                cantidad_text = card.find_element_by_css_selector("span.quantity").text.strip()
                cantidad, unidad = cantidad_text.split(" ", 1)
                cantidad = float(cantidad.replace(",", "."))
                
                productos.append({
                    "nombre": nombre,
                    "cantidad": cantidad,
                    "unidad": unidad,
                    "precio_unitario": precio
                })
            except Exception:
                continue

        for prod in productos:
            res_prod = supabase.table("producto").upsert(
                [{"nombre": prod["nombre"], "cantidad": prod["cantidad"], "unidad": prod["unidad"]}],
                on_conflict="nombre"
            ).execute()
            if not res_prod.data:
                continue
            id_producto = res_prod.data[0]["id_producto"]

            supabase.table("supermercadoproducto").upsert(
                [{
                    "id_supermercado": id_supermercado,
                    "id_producto": id_producto,
                    "precio_unitario": prod["precio_unitario"]
                }],
                on_conflict=["id_supermercado", "id_producto"]
            ).execute()

    finally:
        driver.quit()
