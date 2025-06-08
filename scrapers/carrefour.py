import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    # Añade un directorio temporal para evitar conflictos con perfiles
    user_data_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={user_data_dir}")

    return webdriver.Chrome(options=options)

def scroll_to_bottom(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def get_category_links(driver):
    driver.get("https://www.carrefour.es/supermercado")
    time.sleep(5)
    links = set()
    menu_items = driver.find_elements(By.CSS_SELECTOR, "a.css-1j8o68f")
    for item in menu_items:
        href = item.get_attribute("href")
        if href and "/supermercado/" in href:
            links.add(href)
    return list(links)

def get_or_create_supermercado(supabase):
    res = supabase.table("supermercado").upsert([{"nombre": "Carrefour"}], on_conflict="nombre").execute()
    if res.data:
        return res.data[0]["id_supermercado"]
    raise Exception("No se pudo crear o obtener Carrefour")

def insert_product(supabase, prod, id_supermercado):
    # Inserta o actualiza el producto
    res = supabase.table("producto").upsert(
        [{
            "nombre": prod["nombre"],
            "cantidad": prod["cantidad"],
            "unidad": prod["unidad"]
        }],
        on_conflict="nombre"
    ).execute()

    if not res.data:
        return

    id_producto = res.data[0]["id_producto"]

    # Relacion supermercado-producto con precio
    supabase.table("supermercadoproducto").upsert(
        [{
            "id_supermercado": id_supermercado,
            "id_producto": id_producto,
            "precio_unitario": prod["precio_unitario"]
        }],
        on_conflict=["id_supermercado", "id_producto"]
    ).execute()

def scrape_category(driver, url):
    print(f"🛒 Scrapeando: {url}")
    driver.get(url)
    time.sleep(5)
    scroll_to_bottom(driver)

    productos = []
    cards = driver.find_elements(By.CSS_SELECTOR, "div.product-tile")
    for card in cards:
        try:
            nombre = card.find_element(By.CSS_SELECTOR, "h3.product-name").text.strip()
            precio_text = card.find_element(By.CSS_SELECTOR, "span.price").text.strip().replace("€", "").replace(",", ".")
            precio = float(precio_text)
            cantidad_text = card.find_element(By.CSS_SELECTOR, "span.quantity").text.strip()
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
    print(f"➡️ {len(productos)} productos encontrados")
    return productos

def scrape_and_upload_carrefour():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    id_supermercado = get_or_create_supermercado(supabase)
    driver = get_driver()

    try:
        categorias = get_category_links(driver)
        print(f"🔗 {len(categorias)} categorías encontradas")

        for url in categorias:
            productos = scrape_category(driver, url)
            for prod in productos:
                insert_product(supabase, prod, id_supermercado)

    finally:
        driver.quit()
        print("✅ Scraping completado y datos subidos a Supabase.")

# Ejecutar
scrape_and_upload_carrefour()

