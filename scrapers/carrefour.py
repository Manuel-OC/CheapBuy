import re
import requests
from bs4 import BeautifulSoup
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

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
    return 1, 'ud'

def scrape_mercadona():
    url = "https://www.mercadona.es/es/ofertas"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    productos_html = soup.select("div.product-item")  # Ajustar selector si cambia
    productos = []
    for p in productos_html:
        nombre_tag = p.select_one("h3.product-item__title")
        precio_tag = p.select_one("span.product-item__price-amount")

        if nombre_tag and precio_tag:
            nombre = nombre_tag.get_text(strip=True)
            precio_str = precio_tag.get_text(strip=True).replace('€', '').replace(',', '.').strip()
            try:
                precio = float(precio_str)
                productos.append((nombre, precio))
            except:
                continue
    return productos

def scrape_and_upsert():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    supermercado_nombre = "Mercadona"
    res = supabase.from_('supermercado').select('id_supermercado').eq('nombre', supermercado_nombre).execute()
    if res.data:
        id_supermercado = res.data[0]['id_supermercado']
    else:
        res = supabase.from_('supermercado').insert({'nombre': supermercado_nombre}).select('id_supermercado').execute()
        id_supermercado = res.data[0]['id_supermercado']

    productos = scrape_mercadona()

    for nombre, precio in productos:
        cantidad, unidad = parse_cantidad_unidad(nombre)

        res = supabase.from_('producto')\
            .select('id_producto')\
            .eq('nombre', nombre)\
            .eq('cantidad', cantidad)\
            .eq('unidad', unidad).execute()
        if res.data:
            id_producto = res.data[0]['id_producto']
        else:
            res = supabase.from_('producto').insert({
                'nombre': nombre,
                'cantidad': cantidad,
                'unidad': unidad
            }).select('id_producto').execute()
            id_producto = res.data[0]['id_producto']

        supabase.from_('supermercadoproducto').upsert({
            'id_supermercado': id_supermercado,
            'id_producto': id_producto,
            'precio_unitario': precio
        }).execute()
