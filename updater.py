from config import SUPABASE_URL, SUPABASE_KEY
from scrapers.dia_scraper import scrape_dia
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def main():
    data = scrape_dia()
    for nombre, precio_u, precio_r in data:
        # Obtener o insertar producto
        res = supabase.table("producto").select("id_producto").eq("nombre", nombre).execute()
        if res.data:
            id_producto = res.data[0]["id_producto"]
        else:
            ins = supabase.table("producto").insert({"nombre": nombre}).execute()
            id_producto = ins.data[0]["id_producto"]

        # Insertar o actualizar precio
        supabase.table("supermercadoproducto").upsert({
            "id_supermercado": 1,
            "id_producto": id_producto,
            "precio_unitario": precio_u,
            "precio_relativo": precio_r or 0
        }).execute()
