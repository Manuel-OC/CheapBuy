from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import psycopg2
import re

DB_HOST = 'localhost'
DB_NAME = 'tu_db'
DB_USER = 'tu_user'
DB_PASS = 'tu_pass'

ID_CARREFOUR = 3

def connect_db():
    return psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)

def upsert_producto(conn, nombre, cantidad, unidad):
    cur = conn.cursor()
    cur.execute("""
        SELECT id_producto FROM producto WHERE nombre=%s AND cantidad=%s AND unidad=%s
    """, (nombre, cantidad, unidad))
    res = cur.fetchone()
    if res:
        id_producto = res[0]
    else:
        cur.execute("""
            INSERT INTO producto (nombre, cantidad, unidad) VALUES (%s, %s, %s) RETURNING id_producto
        """, (nombre, cantidad, unidad))
        id_producto = cur.fetchone()[0]
        conn.commit()
    cur.close()
    return id_producto

def upsert_supermercado_producto(conn, id_supermercado, id_producto, precio_unitario):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO supermercadoproducto (id_supermercado, id_producto, precio_unitario)
        VALUES (%s, %s, %s)
        ON CONFLICT (id_supermercado, id_producto)
        DO UPDATE SET precio_unitario = EXCLUDED.precio_unitario
    """, (id_supermercado, id_producto, precio_unitario))
    conn.commit()
    cur.close()

def parse_cantidad_unidad(text):
    text = text.lower().replace(',', '.').strip()
    match = re.match(r"([\d\.]+)\s*([a-z]+)", text)
    if match:
        cantidad = float(match.group(1))
        unidad = match.group(2)
        if unidad in ['uds', 'u', 'unidad', 'unidades']:
            unidad = 'ud'
        return cantidad, unidad
    else:
        return 1.0, 'ud'

def scrape_carrefour():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    conn = connect_db()

    try:
        url = "https://www.carrefour.es/supermercado/cat"
        print("[Carrefour] Accediendo a la web...")
        driver.get(url)
        time.sleep(5)

        categorias = driver.find_elements(By.CSS_SELECTOR, "a.category-link")  # Ajusta el selector
        print(f"[Carrefour] Categorías encontradas: {len(categorias)}")

        for cat in categorias:
            nombre_cat = cat.text.strip()
            href = cat.get_attribute("href")
            print(f"[Carrefour] Procesando categoría: {nombre_cat}")

            driver.get(href)
            time.sleep(5)

            productos = driver.find_elements(By.CSS_SELECTOR, "div.product-card")  # Ajusta selector
            print(f"[Carrefour] Productos encontrados: {len(productos)}")

            for prod in productos:
                try:
                    nombre = prod.find_element(By.CSS_SELECTOR, "a.product-card__title").text.strip()
                    precio_text = prod.find_element(By.CSS_SELECTOR, "span.price").text.strip().replace('€', '').replace(',', '.')
                    precio_unitario = float(precio_text)

                    # Extraer cantidad y unidad del nombre
                    cant_unid_match = re.search(r"(\d+[,.]?\d*)\s*(kg|g|l|ml|ud|uds|unidad|unidades)", nombre.lower())
                    if cant_unid_match:
                        cantidad, unidad = parse_cantidad_unidad(cant_unid_match.group(0))
                    else:
                        cantidad, unidad = 1.0, 'ud'

                    id_producto = upsert_producto(conn, nombre, cantidad, unidad)
                    upsert_supermercado_producto(conn, ID_CARREFOUR, id_producto, precio_unitario)
                    print(f"  [Carrefour] Insertado: {nombre} | {cantidad}{unidad} | {precio_unitario}€")

                except Exception as e:
                    print(f"[Carrefour] Error producto: {e}")

    finally:
        driver.quit()
        conn.close()

if __name__ == "__main__":
    scrape_carrefour()
