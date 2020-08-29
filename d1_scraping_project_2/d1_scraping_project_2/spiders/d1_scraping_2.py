from scrapy import Spider
from scrapy.http import Request

from seleniumwire import webdriver

from time import sleep

from json import loads


driver = webdriver.Firefox()
sleep(2)

class D1Scraping2Spider(Spider):
	name = 'd1_scraping_2'
	allowed_domains = ['miaguila.com']
	start_urls = ['https://www.miaguila.com/tiendas/d1/']

	def parse(self, response):

		categories = response.xpath('//*[@class= "list-parent-categories"]//div[@class= "parent-category"]/a/@href').extract()
		n_cat = 0


		yield Request(url= response.url,
					  callback= self.categ_parse,
					  meta= {'categories': categories,
							 'n_cat': n_cat},
					  dont_filter= True)
		
	def categ_parse(self, response):
		categories = response.meta['categories']
		n_cat = response.meta['n_cat']

		category = categories[n_cat]

		cat_name = category.split('/', 4)[-1].replace('/', '')



		yield Request(url= 'https://www.miaguila.com' + category,
					  callback= self.selenium_parse,
					  meta= {'categories': categories,
							 'n_cat': n_cat,
							 'cat_name': cat_name})


	def selenium_parse(self, response):
		categories = response.meta['categories']
		n_cat = response.meta['n_cat']
		cat_name = response.meta['cat_name']

		driver.get(response.url)
		sleep(3)

		for request in driver.requests:
			if 'products' in request.url and 'application/json' in request.response.headers['Content-Type']:
				json_cat_url = str(request.url)
				
				print()
				print(request, '-------------> json url')
				print()

		json_cat_url = json_cat_url.split('per-page=')[0]

		yield Request(url= json_cat_url + 'per-page=10000',
					  callback= self.json_cat_parse,
					  meta= {'categories': categories,
							 'n_cat': n_cat,
							 'cat_name': cat_name})




	def json_cat_parse(self, response):
		categories = response.meta['categories']
		n_cat = response.meta['n_cat']
		cat_name = response.meta['cat_name']

		jsonresponse = loads(response.body)

		prods = jsonresponse['products']

		for prod in prods:

			prod_name = prod['name']

			normal_price = prod['originalPrice']
			disc_price =prod['price']

			unidades = prod['quantity']

			image_url = prod['imageUrls'][0]

			print('\nCategoria:\t', cat_name,
				  '\n\tProducto:\t', prod_name,
				  '\n\tNormal price:\t', normal_price,
				  '\n\tDiscount price:\t', disc_price,'\n')


			yield {'cat_name': cat_name,
				   'prod_name': prod_name,
				   'normal_price': normal_price,
				   'disc_price': disc_price,
				   'unidades': unidades,
				   'image_url': image_url}


		if n_cat < len(categories)-1:
			n_cat += 1

			yield Request(url = 'https://www.miaguila.com/tiendas/d1/',
					  	  callback= self.categ_parse,
					  	  meta= {'categories': categories,
							 'n_cat': n_cat},
						  dont_filter= True)
		else: 
			print('\n', '='*20,'\n', 'TAL PARECE QUE SE EXTRAJO TODA LA INFORMACION DE LA PAGINA !!','\n', '='*20, '\n')
			driver.quit()





		




