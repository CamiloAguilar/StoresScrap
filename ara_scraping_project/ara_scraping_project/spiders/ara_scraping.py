from scrapy import Spider
from scrapy.http import Request

from json import loads


class AraScrapingSpider(Spider):
	name = 'ara_scraping'
	allowed_domains = ['aratiendas.com']
	start_urls = ['http://aratiendas.com/']

	def parse(self, response):
		print()
		print(response.url)
		print()

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
			
