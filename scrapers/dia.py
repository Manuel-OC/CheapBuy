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
		driver = crear_driver()	
		driver.get(url)
		
		scrolls = 5
		for _ in range(scrolls):
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "search-product-card")))

		# Parsear contenido con BeautifulSoup
		soup = BeautifulSoup(driver.page_source, 'html.parser')
		tarjetas = soup.find_all('div', class_='search-product-card')
			
		for tarjeta in tarjetas:
			nombre = tarjeta.find('p', class_='search-product-card__product-name')
			precio = tarjeta.find('p', class_='search-product-card__active-price')
			unidad = tarjeta.find('p', class_='search-product-card__price-per-unit')

			nombre_texto = nombre.get_text(strip=True) if nombre else "None"
			precio_texto = limpiar_valor(precio.get_text(strip=True)) if precio else 99999
			unidad_texto = limpiar_valor(unidad.get_text(strip=True)) if unidad else 99999

			nombre_texto = nombre_texto.replace(",", ".")
			precio_texto = precio_texto.replace(",", ".")
			unidad_texto = unidad_texto.replace(",", ".")

			print(f"1;{nombre_texto};{precio_texto};{unidad_texto}")
			
		driver.quit()

	except Exception as e:
		driver.quit()

def inicio():

	urls = [
		"https://www.dia.es/freidora-de-aire-airfryer/patatas-airfryer/c/L2231",
		"https://www.dia.es/freidora-de-aire-airfryer/rebozados-airfryer/c/L2232",
		"https://www.dia.es/freidora-de-aire-airfryer/verduras-airfryer/c/L2233",
		"https://www.dia.es/freidora-de-aire-airfryer/pescados-y-mariscos-airfryer/c/L2234",
		"https://www.dia.es/freidora-de-aire-airfryer/carne-airfryer/c/L2235",
		"https://www.dia.es/freidora-de-aire-airfryer/comida-preparada-airfryer/c/L2236",
		"https://www.dia.es/freidora-de-aire-airfryer/accesorios-airfryer/c/L2237",

		"https://www.dia.es/charcuteria-y-quesos/jamon-cocido-lacon-fiambres-y-mortadela/c/L2001",
		"https://www.dia.es/charcuteria-y-quesos/jamon-curado-y-paleta/c/L2004",
		"https://www.dia.es/charcuteria-y-quesos/lomo-chorizo-fuet-salchichon/c/L2005",
		"https://www.dia.es/charcuteria-y-quesos/queso-curado-semicurado-y-tierno/c/L2007",
		"https://www.dia.es/charcuteria-y-quesos/queso-fresco/c/L2008",
		"https://www.dia.es/charcuteria-y-quesos/queso-azul-y-roquefort/c/L2009",
		"https://www.dia.es/charcuteria-y-quesos/quesos-fundidos-y-cremas/c/L2010",
		"https://www.dia.es/charcuteria-y-quesos/quesos-internacionales/c/L2011",
		"https://www.dia.es/charcuteria-y-quesos/salchichas/c/L2206",
		"https://www.dia.es/charcuteria-y-quesos/foie-pate-y-sobrasada/c/L2012",

		"https://www.dia.es/carniceria/pollo/c/L2202",
		"https://www.dia.es/carniceria/vacuno/c/L2013",
		"https://www.dia.es/carniceria/cerdo/c/L2014",
		"https://www.dia.es/carniceria/pavo/c/L2015",
		"https://www.dia.es/carniceria/conejo/c/L2016",
		"https://www.dia.es/carniceria/hamburguesas-y-carne-picada/c/L2017",

		"https://www.dia.es/pescados-mariscos-y-ahumados/pescados/c/L2019",
		"https://www.dia.es/pescados-mariscos-y-ahumados/mariscos/c/L2194",
		"https://www.dia.es/pescados-mariscos-y-ahumados/ahumados-salazones-y-preparados/c/L2020",
		"https://www.dia.es/pescados-mariscos-y-ahumados/sucedaneo-de-angulas-y-surimi/c/L2021",

		"https://www.dia.es/verduras/ajos-cebollas-y-puerros/c/L2022",
		"https://www.dia.es/verduras/tomates-pimientos-y-pepinos/c/L2023",
		"https://www.dia.es/verduras/calabacin-calabaza-y-berenjena/c/L2181",
		"https://www.dia.es/verduras/judias-brocolis-y-coliflores/c/L2024",
		"https://www.dia.es/verduras/lechuga-escarolas-y-endivias/c/L2027",
		"https://www.dia.es/verduras/patatas-y-zanahorias/c/L2028",
		"https://www.dia.es/verduras/setas-y-champinones/c/L2029",
		"https://www.dia.es/verduras/verduras-y-ensaladas-preparadas/c/L2030",
		"https://www.dia.es/verduras/otras-verduras/c/L2031",

		"https://www.dia.es/frutas/frutas-de-temporada/c/L2040",
		"https://www.dia.es/frutas/manzanas/c/L2032",
		"https://www.dia.es/frutas/platanos/c/L2033",
		"https://www.dia.es/frutas/peras/c/L2034",
		"https://www.dia.es/frutas/naranjas-y-mandarinas/c/L2196",
		"https://www.dia.es/frutas/uvas/c/L2035",
		"https://www.dia.es/frutas/limones-y-pomelos/c/L2037",
		"https://www.dia.es/frutas/frutas-del-bosque/c/L2038",
		"https://www.dia.es/frutas/frutas-tropicales/c/L2039",
		"https://www.dia.es/frutas/frutas-deshidratadas/c/L2041",

		"https://www.dia.es/leche-huevos-y-mantequilla/leche/c/L2051",
		"https://www.dia.es/leche-huevos-y-mantequilla/bebidas-vegetales/c/L2052",
		"https://www.dia.es/leche-huevos-y-mantequilla/batidos-y-horchatas/c/L2053",
		"https://www.dia.es/leche-huevos-y-mantequilla/huevos/c/L2055",
		"https://www.dia.es/leche-huevos-y-mantequilla/mantequilla-y-margarina/c/L2056",
		"https://www.dia.es/leche-huevos-y-mantequilla/nata/c/L2054",

		"https://www.dia.es/yogures-y-postres/griegos-y-mousse/c/L2082",
		"https://www.dia.es/yogures-y-postres/yogures-naturales/c/L2079",
		"https://www.dia.es/yogures-y-postres/yogures-de-sabores-y-frutas/c/L2081",
		"https://www.dia.es/yogures-y-postres/yogures-infantiles/c/L2083",
		"https://www.dia.es/yogures-y-postres/yogures-desnatados/c/L2080",
		"https://www.dia.es/yogures-y-postres/yogures-bifidus-y-colesterol/c/L2078",
		"https://www.dia.es/yogures-y-postres/yogures-de-soja-y-enriquecidos/c/L2084",
		"https://www.dia.es/yogures-y-postres/kefir-y-otros-yogures/c/L2085",
		"https://www.dia.es/yogures-y-postres/postres-y-yogures-de-proteinas/c/L2229",
		"https://www.dia.es/yogures-y-postres/natillas-y-flan/c/L2088",
		"https://www.dia.es/yogures-y-postres/arroz-con-leche-y-postre-tradicional/c/L2087",
		"https://www.dia.es/yogures-y-postres/cuajada/c/L2086",
		"https://www.dia.es/yogures-y-postres/gelatinas-y-otros-postres/c/L2089",

		"https://www.dia.es/arroz-pastas-y-legumbres/arroz/c/L2042",
		"https://www.dia.es/arroz-pastas-y-legumbres/pastas/c/L2044",
		"https://www.dia.es/arroz-pastas-y-legumbres/garbanzos/c/L2191",
		"https://www.dia.es/arroz-pastas-y-legumbres/alubias/c/L2178",
		"https://www.dia.es/arroz-pastas-y-legumbres/lentejas/c/L2193",
		"https://www.dia.es/arroz-pastas-y-legumbres/quinoa-y-couscous/c/L2043",

		"https://www.dia.es/aceites-salsas-y-especias/aceites/c/L2046",
		"https://www.dia.es/aceites-salsas-y-especias/vinagres-y-alinos/c/L2047",
		"https://www.dia.es/aceites-salsas-y-especias/tomate/c/L2208",
		"https://www.dia.es/aceites-salsas-y-especias/mayonesa-ketchup-y-otras-salsas/c/L2050",
		"https://www.dia.es/aceites-salsas-y-especias/sal-y-especias/c/L2048",

		"https://www.dia.es/conservas-caldos-y-cremas/atun-bonito-y-caballa/c/L2179",
		"https://www.dia.es/conservas-caldos-y-cremas/berberechos/c/L2180",
		"https://www.dia.es/conservas-caldos-y-cremas/mejillones/c/L2195",
		"https://www.dia.es/conservas-caldos-y-cremas/sardinas-y-sardinillas/c/L2207",
		"https://www.dia.es/conservas-caldos-y-cremas/otras-conservas-de-pescado/c/L2197",
		"https://www.dia.es/conservas-caldos-y-cremas/conservas-vegetales/c/L2092",
		"https://www.dia.es/conservas-caldos-y-cremas/sopas-caldos-y-pures-deshidratados/c/L2093",
		"https://www.dia.es/conservas-caldos-y-cremas/cremas-y-caldos-liquidos/c/L2094",

		"https://www.dia.es/panes-harinas-y-masas/pan-recien-horneado/c/L2070",
		"https://www.dia.es/panes-harinas-y-masas/pan-de-molde-perritos-y-hamburguesas/c/L2069",
		"https://www.dia.es/panes-harinas-y-masas/picos-y-panes-tostados/c/L2071",
		"https://www.dia.es/panes-harinas-y-masas/pan-rallado/c/L2072",
		"https://www.dia.es/panes-harinas-y-masas/harinas-y-levaduras/c/L2075",
		"https://www.dia.es/panes-harinas-y-masas/masas-y-hojaldres/c/L2076",
		"https://www.dia.es/panes-harinas-y-masas/preparados-para-postres/c/L2077",

		"https://www.dia.es/cafe-cacao-e-infusiones/cafe/c/L2057",
		"https://www.dia.es/cafe-cacao-e-infusiones/cacao/c/L2058",
		"https://www.dia.es/cafe-cacao-e-infusiones/te-e-infusiones/c/L2059",

		"https://www.dia.es/azucar-chocolates-y-caramelos/azucar-y-edulcorantes/c/L2060",
		"https://www.dia.es/azucar-chocolates-y-caramelos/miel/c/L2061",
		"https://www.dia.es/azucar-chocolates-y-caramelos/mermeladas-y-frutas-en-almibar/c/L2062",
		"https://www.dia.es/azucar-chocolates-y-caramelos/cremas-de-cacao/c/L2228",
		"https://www.dia.es/azucar-chocolates-y-caramelos/chocolates-y-bombones/c/L2063",
		"https://www.dia.es/azucar-chocolates-y-caramelos/caramelos-chicles-y-golosinas/c/L2064",

		"https://www.dia.es/galletas-bollos-y-cereales/galletas/c/L2065",
		"https://www.dia.es/galletas-bollos-y-cereales/galletas-saladas/c/L2066",
		"https://www.dia.es/galletas-bollos-y-cereales/bolleria/c/L2067",
		"https://www.dia.es/galletas-bollos-y-cereales/cereales/c/L2068",
		"https://www.dia.es/galletas-bollos-y-cereales/tortitas/c/L2216",

		"https://www.dia.es/patatas-fritas-encurtidos-y-frutos-secos/patatas-fritas-y-aperitivos/c/L2098",
		"https://www.dia.es/patatas-fritas-encurtidos-y-frutos-secos/aceitunas-y-encurtidos/c/L2096",
		"https://www.dia.es/patatas-fritas-encurtidos-y-frutos-secos/frutos-secos/c/L2097",

		"https://www.dia.es/pizzas-y-platos-preparados/pizzas/c/L2101",
		"https://www.dia.es/pizzas-y-platos-preparados/precocinados-envasados/c/L2102",
		"https://www.dia.es/pizzas-y-platos-preparados/comida-internacional/c/L2103",
		"https://www.dia.es/pizzas-y-platos-preparados/tortillas-y-empanadas/c/L2105",
		"https://www.dia.es/pizzas-y-platos-preparados/gazpachos-y-salmorejos/c/L2106",

		"https://www.dia.es/congelados/helados-y-hielo/c/L2130",
		"https://www.dia.es/congelados/pizzas-bases-y-masas/c/L2131",
		"https://www.dia.es/congelados/pescado-y-marisco/c/L2132",
		"https://www.dia.es/congelados/carne-y-pollo/c/L2133",
		"https://www.dia.es/congelados/verduras-hortalizas-y-salteados/c/L2210",
		"https://www.dia.es/congelados/patatas-fritas/c/L2213",
		"https://www.dia.es/congelados/croquetas-y-rebozados/c/L2135",
		"https://www.dia.es/congelados/churros-y-postres/c/L2136",
		"https://www.dia.es/congelados/lasanas-y-pasta/c/L2137",

		"https://www.dia.es/agua-refrescos-y-zumos/agua/c/L2107",
		"https://www.dia.es/agua-refrescos-y-zumos/cola/c/L2108",
		"https://www.dia.es/agua-refrescos-y-zumos/naranja/c/L2212",
		"https://www.dia.es/agua-refrescos-y-zumos/limon-lima-limon/c/L2109",
		"https://www.dia.es/agua-refrescos-y-zumos/tes-frios-cafes-frios/c/L2111",
		"https://www.dia.es/agua-refrescos-y-zumos/tonicas/c/L2112",
		"https://www.dia.es/agua-refrescos-y-zumos/gaseosa/c/L2192",
		"https://www.dia.es/agua-refrescos-y-zumos/bebidas-energeticas/c/L2217",
		"https://www.dia.es/agua-refrescos-y-zumos/bebidas-isotonicas/c/L2114",
		"https://www.dia.es/agua-refrescos-y-zumos/zumos/c/L2113",
		"https://www.dia.es/agua-refrescos-y-zumos/otras-bebidas/c/L2110",

		"https://www.dia.es/cervezas-vinos-y-bebidas-con-alcohol/cervezas/c/L2115",
		"https://www.dia.es/cervezas-vinos-y-bebidas-con-alcohol/cervezas-especiales/c/L2117",
		"https://www.dia.es/cervezas-vinos-y-bebidas-con-alcohol/cervezas-con-limon/c/L2182",
		"https://www.dia.es/cervezas-vinos-y-bebidas-con-alcohol/cervezas-sin-alcohol/c/L2118",
		"https://www.dia.es/cervezas-vinos-y-bebidas-con-alcohol/tinto-de-verano-y-sangria/c/L2119",
		"https://www.dia.es/cervezas-vinos-y-bebidas-con-alcohol/vino-tinto/c/L2120",
		"https://www.dia.es/cervezas-vinos-y-bebidas-con-alcohol/vino-blanco/c/L2121",
		"https://www.dia.es/cervezas-vinos-y-bebidas-con-alcohol/cavas-y-sidra/c/L2122",
		"https://www.dia.es/cervezas-vinos-y-bebidas-con-alcohol/vino-rosado/c/L2124",
		"https://www.dia.es/cervezas-vinos-y-bebidas-con-alcohol/ginebra-y-vodka/c/L2125",
		"https://www.dia.es/cervezas-vinos-y-bebidas-con-alcohol/ron-y-whisky/c/L2128",
		"https://www.dia.es/cervezas-vinos-y-bebidas-con-alcohol/vermouth/c/L2127",
		"https://www.dia.es/cervezas-vinos-y-bebidas-con-alcohol/cremas-y-licores/c/L2129",
		"https://www.dia.es/cervezas-vinos-y-bebidas-con-alcohol/brandy/c/L2126",

		"https://www.dia.es/limpieza-y-hogar/cuidado-de-la-ropa/c/L2170",
		"https://www.dia.es/limpieza-y-hogar/lavavajillas/c/L2167",
		"https://www.dia.es/limpieza-y-hogar/papel-higienico-de-cocina-servilletas/c/L2168",
		"https://www.dia.es/limpieza-y-hogar/utensilios-de-limpieza/c/L2159",
		"https://www.dia.es/limpieza-y-hogar/bolsas-de-basura/c/L2160",
		"https://www.dia.es/limpieza-y-hogar/lejia-y-otros-quimicos/c/L2161",
		"https://www.dia.es/limpieza-y-hogar/cristales-y-suelos/c/L2162",
		"https://www.dia.es/limpieza-y-hogar/limpia-muebles-y-multiusos/c/L2163",
		"https://www.dia.es/limpieza-y-hogar/limpieza-bano-y-wc/c/L2164",
		"https://www.dia.es/limpieza-y-hogar/limpieza-cocina-y-vitroceramica/c/L2166",
		"https://www.dia.es/limpieza-y-hogar/papel-de-aluminio-horno-y-film/c/L2169",
		"https://www.dia.es/limpieza-y-hogar/insecticidas/c/L2173",
		"https://www.dia.es/limpieza-y-hogar/ambientadores/c/L2226",
		"https://www.dia.es/limpieza-y-hogar/calzado/c/L2171",
		"https://www.dia.es/limpieza-y-hogar/utiles-del-hogar-pilas-bombillas/c/L2209",

		"https://www.dia.es/perfumeria-higiene-salud/hidratacion-corporal/c/L2153",
		"https://www.dia.es/perfumeria-higiene-salud/gel-de-ducha-y-esponjas/c/L2211",
		"https://www.dia.es/perfumeria-higiene-salud/cuidado-bucal/c/L2151",
		"https://www.dia.es/perfumeria-higiene-salud/desodorantes/c/L2154",
		"https://www.dia.es/perfumeria-higiene-salud/champu/c/L2144",
		"https://www.dia.es/perfumeria-higiene-salud/acondicionadores-y-mascarillas/c/L2145",
		"https://www.dia.es/perfumeria-higiene-salud/espumas-y-fijadores/c/L2146",
		"https://www.dia.es/perfumeria-higiene-salud/tintes/c/L2147",
		"https://www.dia.es/perfumeria-higiene-salud/limpieza-facial-crema-facial/c/L2148",
		"https://www.dia.es/perfumeria-higiene-salud/quitaesmalte/c/L2186",
		"https://www.dia.es/perfumeria-higiene-salud/afeitado/c/L2150",
		"https://www.dia.es/perfumeria-higiene-salud/depilacion/c/L2188",
		"https://www.dia.es/perfumeria-higiene-salud/colonias/c/L2155",
		"https://www.dia.es/perfumeria-higiene-salud/jabon-de-manos/c/L2156",
		"https://www.dia.es/perfumeria-higiene-salud/cremas-solares/c/L2227",
		"https://www.dia.es/perfumeria-higiene-salud/compresas-y-cuidado-intimo/c/L2158",
		"https://www.dia.es/perfumeria-higiene-salud/complementos-nutricionales/c/L2183",
		"https://www.dia.es/perfumeria-higiene-salud/parafarmacia/c/L2184",

		"https://www.dia.es/bebe/papilla/c/L2138",
		"https://www.dia.es/bebe/leche-infantil/c/L2139",
		"https://www.dia.es/bebe/potitos-y-tarritos/c/L2141",
		"https://www.dia.es/bebe/yogures-bolsitas-de-frutas-y-snacks/c/L2140",
		"https://www.dia.es/bebe/panales-y-toallitas/c/L2142",
		"https://www.dia.es/bebe/cuidado-del-bebe/c/L2143",

		"https://www.dia.es/mascotas/perros/c/L2174",
		"https://www.dia.es/mascotas/gatos/c/L2175",
		"https://www.dia.es/mascotas/otros-animales/c/L2176"
	]

	NUM_HILOS = psutil.cpu_count(logical=False)

	with ThreadPoolExecutor(max_workers=NUM_HILOS) as executor:
		executor.map(scrape_url, urls)
	
inicio()
