from config import DATABASE_URL, SUPER_MAP
from scrapers.dia_scraper import scrape_dia
import psycopg2

def main():
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    cur = conn.cursor()
    supermercado_id = 1  # O puedes mapear desde SUPER_MAP si usas nombres

    data = scrape_dia()
    for nombre, precio_u, precio_r in data:
        cur.execute("INSERT INTO producto (nombre) VALUES (%s) ON CONFLICT (nombre) DO UPDATE SET nombre=EXCLUDED.nombre RETURNING id_producto", (nombre,))
        id_producto = cur.fetchone()[0]
        cur.execute("""
            INSERT INTO supermercadoproducto (id_supermercado, id_producto, precio_unitario, precio_relativo)
            VALUES (%s,%s,%s,%s)
            ON CONFLICT (id_supermercado, id_producto)
            DO UPDATE SET precio_unitario = EXCLUDED.precio_unitario, precio_relativo = EXCLUDED.precio_relativo
        """, (supermercado_id, id_producto, precio_u, precio_r or 0))
    conn.commit()
    cur.close()
    conn.close()
