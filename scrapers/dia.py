import requests
from bs4 import BeautifulSoup
import psycopg2
import re

# Config DB (modifica según tu config)
DB_HOST = 'localhost'
DB_NAME = 'tu_db'
DB_USER = 'tu_user'
DB_PASS = 'tu_pass'

# ID supermercado DIA (asegúrate que exista)
ID_DIA = 2

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
    # Ejemplo: "500 g", "1,5 L", "12 uds", "1 kg"
    # Convertir coma a punto para float
    text = text.lower().replace(',', '.').strip()
    match = re.match(r"([\d\.]+)\s*([a-z]+)", text)
    if match:
        cantidad = float(match.group(1))
        unidad = match.group(2)
        # Normaliza unidad, ej: "uds" -> "ud"
        if unidad in ['uds', 'u', 'unidad', 'unidades']:
            unidad = 'ud'
        return cantidad, unidad
    else:
        # Por defecto, 1 ud
        return 1.0, 'ud'

def scrape_dia():
    base_url = "https://www.dia.es"
    url = f"{base_url}/supermercado/cat"

    headers = {"User-Agent": "Mozilla/5.0"}

    print("[DIA] Obteniendo página de categorías...")
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print(f"[DIA] Error: {res.status_code}")
        return

    soup = BeautifulSoup(res.text, 'html.parser')

    # Ajustar selector según la web real (aquí ejemplo genérico)
    categorias = soup.select("a.category-list__link")
    print(f"[DIA] Categorías encontradas: {len(categorias)}")

    conn = connect_db()

    for cat in categorias:
        nombre_cat = cat.get_text(strip=True)
        url_cat = base_url + cat['href']
        print(f"[DIA] Procesando categoría: {nombre_cat}")

        res_cat = requests.get(url_cat, headers=headers)
        if res_cat.status_code != 200:
            print(f"[DIA] Error al obtener productos categoría {nombre_cat}: {res_cat.status_code}")
            continue

        soup_cat = BeautifulSoup(res_cat.text, 'html.parser')

        productos = soup_cat.select("div.product-tile")
        print(f"[DIA] Productos encontrados en {nombre_cat}: {len(productos)}")

        for prod in productos:
            try:
                nombre = prod.select_one("a.product-tile__title").get_text(strip=True)
                precio_text = prod.select_one("span.price").get_text(strip=True).replace('€', '').replace(',', '.').strip()
                precio_unitario = float(precio_text)

                # Intentar extraer cantidad y unidad del nombre o alguna clase - adaptar según HTML
                # Ejemplo: "Leche Entera 1 L"
                cant_unid_match = re.search(r"(\d+[,.]?\d*)\s*(kg|g|l|ml|ud|uds|unidad|unidades)", nombre.lower())
                if cant_unid_match:
                    cantidad, unidad = parse_cantidad_unidad(cant_unid_match.group(0))
                else:
                    cantidad, unidad = 1.0, 'ud'

                id_producto = upsert_producto(conn, nombre, cantidad, unidad)
                upsert_supermercado_producto(conn, ID_DIA, id_producto, precio_unitario)
                print(f"  [DIA] Insertado: {nombre} | {cantidad}{unidad} | {precio_unitario}€")
            except Exception as e:
                print(f"[DIA] Error procesando producto: {e}")

    conn.close()

if __name__ == "__main__":
    scrape_dia()
