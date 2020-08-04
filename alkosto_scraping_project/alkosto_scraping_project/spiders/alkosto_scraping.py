from scrapy import Spider
from scrapy.http import Request

class AlkostoScrapingSpider(Spider):
	name = 'alkosto_scraping'
	allowed_domains = ['alkosto.com']
	start_urls = ['http://alkosto.com/']


	def parse(self, response):

		try: n_cat = response.meta['n_cat']
		except: n_cat = 0 ####################################################################################################### OJO!! 

		print('\n','#'*20, 'Este es n_cat !!', '\n', n_cat)

		categories =  response.xpath('//*[@class= "outer_ele"]/div/a/@href').extract()

		category = categories[n_cat] 

		if 'llantas' in category:
			category = category.split('/llantas')[0]


		if 'hogar' not in category and 'jugueteria' not in category:
			yield Request(url= category,
						  callback= self.category_parse,
						  meta= {'n_cat': n_cat,
								 'categories': categories,
								 'category': category})
		elif 'hogar' in category:
			yield Request(url= category,
						  callback= self.home_parse,
						  meta= {'n_cat': n_cat,
								 'categories': categories,
								 'category': category})
		else:
			n_cat += 1
			yield Request(url= 'http://alkosto.com/',
						  callback= self.parse,
						  dont_filter= True,
						  meta= {'n_cat': n_cat}) 


	def home_parse(self, response):
		n_cat = response.meta['n_cat']
		categories = response.meta['categories']
		category = response.meta['category']

		try: home_n_cat = response.meta['home_n_cat']
		except: home_n_cat = 0

		sub_categories = response.xpath('//*[@class= "botones-categorias col-12"]/ul/li/a/@href').extract()

		sub_category = sub_categories[home_n_cat]

		yield Request(url= sub_category,
					  callback= self.category_parse,
					  meta= {'home_n_cat': home_n_cat,
							 'sub_categories': sub_categories,
							 'n_cat': n_cat,
							 'categories': categories,
							 'category': category})



	def category_parse(self, response):
		n_cat = response.meta['n_cat']
		categories = response.meta['categories']
		category = response.meta['category']

		try: 
			home_n_cat = response.meta['home_n_cat']
			sub_categories = response.meta['sub_categories']
		except: 
			home_n_cat = 0
			sub_categories = []

		try: pag = response.meta['pag']
		except: pag = 1

		print('\n', response.url, '\n')

		cat_name = response.xpath('//*[@class= "page-title category-title"]/h1/text()').extract_first()

		products = response.xpath('//*[@class = "category-products"]/ul/li')
		
		for product in products:

			print('\n', '*'*20, 'Estamos en la pagina ', pag, ' de la categoria de ', cat_name, '*'*20, '\n')
			
			prod_name = product.xpath('.//*[@class= "product-name"]/a/text()').extract_first().strip()
			
			try:
				disc_price =  product.xpath('.//*[@class= "price-box"]/p/span/*[@class = "price"]//text()').extract_first().strip()
			except:
				disc_price =product.xpath('.//*[@class= "price-box"]/span[@class= "regular-price"]//text()').extract()[2]
			
			try:
				normal_price = product.xpath('.//*[@class= "price-box"]/p/span[@class = "price-old"]/text()').extract_first().strip()
			except:
				normal_price = disc_price
			image_url = product.xpath('.//*[@class= "amlabel-div"]/a/img/@data-src').extract_first()

			print('\n', '#'*15, 'Resultado Producto', '#'*15, '\n')
			print('Categoria: ', cat_name, '\n',
				  '\n\tProducto:\t', prod_name,
				  '\n\tPrecio norm:\t', normal_price,
				  '\n\tPrecio desc:\t', disc_price)

		
			yield {'cat_name': cat_name,
				   'prod_name': prod_name,
				   'normal_price': normal_price,
				   'disc_price': disc_price,
				   'image_url': image_url}


		next_pag = response.xpath('//*[@class= "next i-next"]').extract()
		
		if next_pag != []:
			pag += 1
			yield Request(url= category + '?p=' + str(pag),
						 callback= self.category_parse,
						 meta= {'n_cat': n_cat,
								'categories': categories,
								'category': category,
								'home_n_cat': home_n_cat,
								'sub_categories': sub_categories,
								'home_n_cat': home_n_cat,
								'sub_categories': sub_categories,
								'pag': pag},
						dont_filter= True)




		elif n_cat < len(categories) - 1:

			if 'hogar' in response.url and home_n_cat < len(sub_categories) - 1:
				home_n_cat += 1
				yield Request(url= 'https://www.alkosto.com/hogar',
							  callback= self.home_parse,
							  meta = {'home_n_cat': home_n_cat,
							  		  'n_cat': n_cat,
							  		  'categories': categories,
							  		  'category': category},
							  dont_filter= True)
			
			else:
				n_cat += 1
				yield Request(url= 'http://alkosto.com/',
							  callback= self.parse,
							  dont_filter= True,
							  meta= {'n_cat': n_cat}) 

		else:
			print('\n', '='*20,'\n', 'TAL PARECE QUE SE EXTRAJO TODA LA INFORMACION DE LA PAGINA !!','\n', '='*20, '\n')