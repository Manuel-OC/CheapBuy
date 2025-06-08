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
    # NO user-data-dir para evitar conflicto
    driver = webdriver.Chrome(options=options)
    return driver

def get_or_create_supermercado(supabase):
    # Inserta o recupera supermercado Mercadona
    data = [{"nombre": "Mercadona"}]
    res = supabase.table("supermercado").upsert(data, on_conflict="nombre").execute()
    if res.data:
        return res.data[0]["id_supermercado"]
    raise Exception("No se pudo crear o obtener Mercadona")

def scrape_and_upsert():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    id_supermercado = get_or_create_supermercado(supabase)

    driver = get_driver()
    try:
        driver.get("https://www.mercadona.es/es/ofertas")
        time.sleep(5)  # espera a que cargue JS

        productos = []
        cards = driver.find_elements_by_css_selector("div.product-card")  # Ajusta selector según página
        for card in cards:
            try:
                nombre = card.find_element_by_css_selector("h2.product-name").text.strip()
                precio_text = card.find_element_by_css_selector("span.price").text.strip().replace("€", "").replace(",", ".")
                precio = float(precio_text)
                cantidad_text = card.find_element_by_css_selector("span.quantity").text.strip()
                # Asume formato "500 g" o "1 L"
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
            # Insertar producto
            res_prod = supabase.table("producto").upsert(
                [{"nombre": prod["nombre"], "cantidad": prod["cantidad"], "unidad": prod["unidad"]}],
                on_conflict="nombre"
            ).execute()
            if not res_prod.data:
                continue
            id_producto = res_prod.data[0]["id_producto"]

            # Insertar relacion supermercado-producto con precio
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
