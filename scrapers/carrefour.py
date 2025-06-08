import time
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

def get_driver():
    profile_dir = tempfile.mkdtemp()
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(f"--user-data-dir={profile_dir}")
    options.add_argument("--incognito")
    options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(options=options)
    return driver

def get_or_create_supermercado(supabase):
    data = [{"nombre": "Carrefour"}]
    res = supabase.table("supermercado").upsert(data, on_conflict="nombre").execute()
    return res.data[0]["id_supermercado"]

def scrape_and_upsert():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    id_supermercado = get_or_create_supermercado(supabase)

    driver = get_driver()
    try:
        driver.get("https://www.carrefour.es/supermercado/")
        time.sleep(5)

        productos = []
        cards = driver.find_elements(By.CSS_SELECTOR, "div.product-tile")
        for card in cards:
            try:
                nombre = card.find_element(By.CSS_SELECTOR, "h3.product-name").text.strip()
                precio_text = card.find_element(By.CSS_SELECTOR, "span.price").text.strip()
                precio = float(precio_text.replace("€", "").replace(",", "."))
                cantidad_text = card.find_element(By.CSS_SELECTOR, "span.quantity").text.strip()
                cantidad, unidad = cantidad_text.split(" ", 1)
                cantidad = float(cantidad.replace(",", "."))
                productos.append({
                    "nombre": nombre,
                    "cantidad": cantidad,
                    "unidad": unidad,
                    "precio_unitario": precio
                })
            except:
                continue

        for prod in productos:
            supabase.table("producto").upsert(
                {
                    "nombre": prod["nombre"],
                    "cantidad": prod["cantidad"],
                    "unidad": prod["unidad"]
                },
                on_conflict=["nombre", "cantidad", "unidad"]
            ).execute()
            res_p = supabase.table("producto").select("id_producto")\
                .match({
                    "nombre": prod["nombre"],
                    "cantidad": prod["cantidad"],
                    "unidad": prod["unidad"]
                }).execute()
            id_producto = res_p.data[0]["id_producto"]
            supabase.table("supermercadoproducto").upsert(
                {
                    "id_supermercado": id_supermercado,
                    "id_producto": id_producto,
                    "precio_unitario": prod["precio_unitario"]
                },
                on_conflict=["id_supermercado", "id_producto"]
            ).execute()
    finally:
        driver.quit()
