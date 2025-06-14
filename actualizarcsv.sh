#!/bin/bash

echo "idsupermercado;nombreproducto;precioproducto;precioporunidadproducto" > cheapbuy.csv

echo "SCRAPEANDO DIA..."
python3 ./scrapers/dia.py >> cheapbuy.csv
echo "DIA SCRAPEADO!"

echo "SCRAPEANDO MERCADONA..."
php ./scrapers/mercadona.php >> cheapbuy.csv
echo "MERCADONA SCRAPEADO!"

echo "SCRAPEANDO CARREFOUR..."
python3 ./scrapers/carrefour.py >> cheapbuy.csv
echo "CARREFOUR SCRAPEADO!"
