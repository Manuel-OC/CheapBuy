<?php

scraper_mercadona();

function scraper_mercadona() {
	$ch = curl_init();
	curl_setopt($ch, CURLOPT_URL, 'https://tienda.mercadona.es/api/categories/'); 
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true); 
	curl_setopt($ch, CURLOPT_HEADER, 0); 
	$data = curl_exec($ch); 
	curl_close($ch); 

	if ( $data ) {
		$categorias = json_decode($data);
         
		if ( isset($categorias->results) ) {           
			foreach ( $categorias->results as $category ) {
				foreach ( $category->categories as $i ) {
					get_productos($i->id);
				}
			}
		}
	}
}

function get_productos( $category_id ) {
	$ch = curl_init();
	curl_setopt($ch, CURLOPT_URL, 'https://tienda.mercadona.es/api/categories/' . $category_id); 
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true); 
	curl_setopt($ch, CURLOPT_HEADER, 0); 
	$data = curl_exec($ch); 
	curl_close($ch); 
      
	if ( $data ) {
		$category = json_decode($data);
		if ( isset($category->categories) ) {
			foreach ( $category->categories as $cat_info ) {
				if ( isset($cat_info->products) ) {
					foreach ( $cat_info->products as $product ) {
						$nombre = str_replace(',', '.', $product->display_name ?? "None");
						$precio = str_replace(',', '.', $product->price_instructions->unit_price ?? 99999);
						$unidad = str_replace(',', '.', $product->price_instructions->bulk_price ?? 99999);

						echo "2;".$nombre.";".$precio.";".$unidad."\n";
					}
				}
				get_productos($cat_info->id);
			}
		}
	}
}
?>
