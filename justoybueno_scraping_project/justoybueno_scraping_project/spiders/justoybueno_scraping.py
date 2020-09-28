from scrapy import Spider
from scrapy.http import Request

from json import loads

from pandas import read_csv

from time import sleep
from socket import gethostbyname, create_connection, error



def check_connection():
	while True:
		try:
			gethostbyname('google.com')
			connection = create_connection(('google.com', 80), 1)
			connection.close()
			print('Hay conexion a internet, continuamos !!')
			break
		
		except error:
			print('No hay conexion a internet, esperaremos por 2 minutos')
			sleep(120)
			continue


check_connection()

class JustoybuenoScrapingSpider(Spider):
	name = 'justoybueno_scraping'
	allowed_domains = ['justoybueno.com']
	start_urls = ['http://justoybueno.com/']

	def parse(self, response):
		print()
		print(response.url)
		print()

		cod_dane = read_csv('codigos_dane.csv', dtype= {'cod_municipio': str})
		#print(cod_dane)
		for cod in cod_dane['cod_municipio']:
			
			check_connection()
			yield Request(url= 'https://monedero.justoybueno.com/servicios/api/public/Producto/GetProductosMarcados?codCiudad=' + cod,
						  callback= self.mun_prod_parse,
						  meta= {'cod': cod})

	def mun_prod_parse(self, response):
		cod = response.meta['cod']
		if response.body != b'[]':
			jesonresponse = loads(response.body)

			for prod in jesonresponse:
				cat_name = prod['categoria']
				prod_name = prod['descripcion']

				normal_price= prod['precio']
				disc_price= prod['precio']

				image_url = prod['imageUrl']

				print('\nCategoria:\t', cat_name,
					  '\n\tProducto:\t', prod_name,
					  '\n\tNormal price:\t', normal_price,
					  '\n\tDiscount price:\t', disc_price,'\n')


				yield {'cod': cod,
					   'cat_name': cat_name,
					   'prod_name': prod_name,
					   'normal_price': normal_price,
					   'disc_price': disc_price,
					   'image_url': image_url}