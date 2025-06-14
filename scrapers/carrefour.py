from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time
import psutil
import re

def crear_driver():
	options = Options()
	options.add_argument("--headless")
	options.add_argument("--disable-blink-features=AutomationControlled")
	options.add_argument("--window-size=1920,1080")
	options.add_argument("--lang=es-ES")
	options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
	return webdriver.Chrome(options=options)

def limpiar_valor(valor):
	return re.sub(r"[^\d,]", "", valor)

def scrape_url(url):
	
	try:
		offset = 0
		
		while True:
			driver = crear_driver()	
			driver.get(f"{url}?offset={offset}")
			
			scrolls = 5
			for _ in range(scrolls):
				driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
				WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "product-card")))

			if not driver.current_url.startswith(url):
				break

			# Parsear contenido con BeautifulSoup
			soup = BeautifulSoup(driver.page_source, 'html.parser')
			tarjetas = soup.find_all('div', class_='product-card')
			
			for tarjeta in tarjetas:
				nombre = tarjeta.find('a', class_='product-card__title-link')
				precio = tarjeta.find('span', class_='product-card__price')
				unidad = tarjeta.find('span', class_='product-card__price-per-unit')

				nombre_texto = nombre.get_text(strip=True) if nombre else "None"

				nombre_texto = nombre_texto.lower()
				nombre_texto = nombre_texto.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
				
				precio_texto = limpiar_valor(precio.get_text(strip=True)) if precio else 99999
				unidad_texto = limpiar_valor(unidad.get_text(strip=True)) if unidad else 99999

				nombre_texto = nombre_texto.replace(",", ".")
				precio_texto = precio_texto.replace(",", ".")
				unidad_texto = unidad_texto.replace(",", ".")

				print(f"3;{nombre_texto};{precio_texto};{unidad_texto}")
			
			offset += 24
			
			driver.quit()

	except Exception as e:
		driver.quit()

def inicio():

	urls = [
		'https://www.carrefour.es/supermercado/productos-frescos/verduras-y-hortalizas/cat220014/c',
		'https://www.carrefour.es/supermercado/productos-frescos/charcuteria/cat20017/c',
		'https://www.carrefour.es/supermercado/productos-frescos/quesos/cat20020/c',
		'https://www.carrefour.es/supermercado/productos-frescos/panaderia-tradicional/cat20019/c',
		'https://www.carrefour.es/supermercado/productos-frescos/charcuteria-y-quesos-al-corte/cat510001/c',
		'https://www.carrefour.es/supermercado/productos-frescos/sushi-del-dia/cat10928974/c',
		'https://www.carrefour.es/supermercado/productos-frescos/platos-preparados-cocinados/cat20016/c',
		'https://www.carrefour.es/supermercado/productos-frescos/carniceria/cat20018/c',
		'https://www.carrefour.es/supermercado/productos-frescos/pescaderia/cat20014/c',
		'https://www.carrefour.es/supermercado/productos-frescos/frutas/cat220006/c',

		'https://www.carrefour.es/supermercado/la-despensa/alimentacion/cat20009/c',
		'https://www.carrefour.es/supermercado/la-despensa/lacteos/cat20011/c',
		'https://www.carrefour.es/supermercado/la-despensa/desayuno/cat26100390/c',
		'https://www.carrefour.es/supermercado/la-despensa/yogures-y-postres/cat390008/c',
		'https://www.carrefour.es/supermercado/la-despensa/dulce/cat26100388/c',
		'https://www.carrefour.es/supermercado/la-despensa/panaderia-bolleria-y-pasteleria/cat21319201/c',
		'https://www.carrefour.es/supermercado/la-despensa/conservas-sopas-y-precocinados/cat20013/c',
		'https://www.carrefour.es/supermercado/la-despensa/aperitivos/cat390001/c',
		'https://www.carrefour.es/supermercado/la-despensa/huevos/cat20021/c',

		'https://www.carrefour.es/supermercado/bebidas/cerveza/cat20023/c',
		'https://www.carrefour.es/supermercado/bebidas/bodega/cat20027/c',
		'https://www.carrefour.es/supermercado/bebidas/refrescos/cat650001/c',
		'https://www.carrefour.es/supermercado/bebidas/aguas-y-zumos/cat650002/c',
		'https://www.carrefour.es/supermercado/bebidas/alcoholes/cat20022/c',
		'https://www.carrefour.es/supermercado/bebidas/cava-y-champagne/cat20024/c',
		'https://www.carrefour.es/supermercado/bebidas/licores-y-cremas/cat20025/c',
		'https://www.carrefour.es/supermercado/bebidas/sidra/cat20026/c',

		'https://www.carrefour.es/supermercado/limpieza-y-hogar/cuidado-de-la-ropa/cat20044/c',
		'https://www.carrefour.es/supermercado/limpieza-y-hogar/papel-y-celulosa/cat20046/c',
		'https://www.carrefour.es/supermercado/limpieza-y-hogar/productos-para-cocina/cat20043/c',
		'https://www.carrefour.es/supermercado/limpieza-y-hogar/productos-para-bano/cat20042/c',
		'https://www.carrefour.es/supermercado/limpieza-y-hogar/productos-para-toda-la-casa/cat20045/c',
		'https://www.carrefour.es/supermercado/limpieza-y-hogar/utensilios-de-limpieza/cat20047/c',
		'https://www.carrefour.es/supermercado/limpieza-y-hogar/conservacion-de-alimentos/cat20039/c',
		'https://www.carrefour.es/supermercado/limpieza-y-hogar/ambientadores/cat20036/c',
		'https://www.carrefour.es/supermercado/limpieza-y-hogar/calzado/cat20038/c',
		'https://www.carrefour.es/supermercado/limpieza-y-hogar/menaje/cat20041/c',
		'https://www.carrefour.es/supermercado/limpieza-y-hogar/papeleria/cat260001/c',
		'https://www.carrefour.es/supermercado/limpieza-y-hogar/bazar/cat20037/c',

		'https://www.carrefour.es/supermercado/perfumeria-e-higiene/bano-e-higiene-corporal/cat20028/c',
		'https://www.carrefour.es/supermercado/perfumeria-e-higiene/cabello/cat20031/c',
		'https://www.carrefour.es/supermercado/perfumeria-e-higiene/cuidado-y-proteccion-corporal/cat20033/c',
		'https://www.carrefour.es/supermercado/perfumeria-e-higiene/depilacion-y-afeitado/cat20034/c',
		'https://www.carrefour.es/supermercado/perfumeria-e-higiene/boca-y-sonrisa/cat20030/c',
		'https://www.carrefour.es/supermercado/perfumeria-e-higiene/higiene-intima/cat20035/c',
		'https://www.carrefour.es/supermercado/perfumeria-e-higiene/cosmetica/cat20032/c',
		'https://www.carrefour.es/supermercado/perfumeria-e-higiene/bienestar-sexual/cat20029/c',

		'https://www.carrefour.es/supermercado/congelados/rebozados-y-platos-preparados/cat21449190/c',
		'https://www.carrefour.es/supermercado/congelados/pizzas-congeladas/cat21449183/c',
		'https://www.carrefour.es/supermercado/congelados/verduras-congeladas/cat21449175/c',
		'https://www.carrefour.es/supermercado/congelados/salteados-congelados/cat21449194/c',
		'https://www.carrefour.es/supermercado/congelados/helados/cat21449202/c',
		'https://www.carrefour.es/supermercado/congelados/mariscos-congelados/cat21449161/c',
		'https://www.carrefour.es/supermercado/congelados/pescados-congelados/cat21449156/c',
		'https://www.carrefour.es/supermercado/congelados/surimi-congelado/cat21449169/c',
		'https://www.carrefour.es/supermercado/congelados/pulpo-calamar-y-sepia-congelados/cat21449164/c',

		'https://www.carrefour.es/supermercado/bebe/panales-y-toallitas/cat20050/c',
		'https://www.carrefour.es/supermercado/bebe/alimentacion-infantil/cat20048/c',
		'https://www.carrefour.es/supermercado/bebe/perfumeria-e-higiene/cat20049/c',
		'https://www.carrefour.es/supermercado/bebe/embarazo-y-lactancia/cat400001/c',
		'https://www.carrefour.es/supermercado/bebe/puericultura/cat400002/c',

		'https://www.carrefour.es/supermercado/mascotas/perros/cat20057/c',
		'https://www.carrefour.es/supermercado/mascotas/gatos/cat20054/c',
		'https://www.carrefour.es/supermercado/mascotas/conejos-y-roedores/cat20053/c',
		'https://www.carrefour.es/supermercado/mascotas/pajaros/cat20055/c',
		'https://www.carrefour.es/supermercado/mascotas/peces-y-tortugas/cat20056/c',

		'https://www.carrefour.es/supermercado/parafarmacia/botiquin/cat20059/c',
		'https://www.carrefour.es/supermercado/parafarmacia/cuidado-corporal/cat20061/c',
		'https://www.carrefour.es/supermercado/parafarmacia/cuidado-e-higiene-facial/cat20062/c',
		'https://www.carrefour.es/supermercado/parafarmacia/cabello/cat20060/c',
		'https://www.carrefour.es/supermercado/parafarmacia/cuidado-de-manos-y-pies/cat20063/c',
		'https://www.carrefour.es/supermercado/parafarmacia/nutricion-y-dietetica/cat20065/c',
		'https://www.carrefour.es/supermercado/parafarmacia/bebe/cat20051/c',
		'https://www.carrefour.es/supermercado/parafarmacia/higiene-bucal/cat20064/c'
	]

	NUM_HILOS = psutil.cpu_count(logical=False)

	with ThreadPoolExecutor(max_workers=NUM_HILOS) as executor:
		executor.map(scrape_url, urls)
	
inicio()
