from scrapy import Spider
from scrapy.http import Request

from json import loads

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

class AraScrapingSpider(Spider):
	name = 'ara_scraping'
	allowed_domains = ['aratiendas.com']
	start_urls = ['http://aratiendas.com/']

	def parse(self, response):
		print()
		print(response.url)
		print()

		check_connection()
		yield Request(url= 'https://api01.inoutdelivery.com.co/v1/products/by-category?business=ara.inoutdelivery.com&pointSale=&limitProducts=1000',
					  callback= self.other_parse,
					  dont_filter= True)

	def other_parse(self, response):
		#print(response.body)

		if response.body != b'[]':
			jsonresponse = loads(response.body)

			for cat in jsonresponse:
				for prod in cat['products']:

					cat_name = cat['name']

					prod = prod['product']

					prod_name = prod['name']

					normal_price = prod['priceOld']

					if normal_price == 0 or normal_price == None:
						disc_price = prod['price']
						normal_price = prod['price']

					else:
						disc_price = prod['price']
						normal_price = prod['priceOld']


					image_url = prod['image']['xs']

					print('\nCategoria:\t', cat_name,
						  '\n\tProducto:\t', prod_name,
						  '\n\tNormal price:\t', normal_price,
						  '\n\tDiscount price:\t', disc_price,'\n')


					yield {'cat_name': cat_name,
						   'prod_name': prod_name,
						   'normal_price': normal_price,
						   'disc_price': disc_price,
						   'image_url': image_url}	
			
