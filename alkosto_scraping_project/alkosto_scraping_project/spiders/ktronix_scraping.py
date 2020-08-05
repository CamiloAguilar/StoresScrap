from scrapy import Spider
from scrapy.http import Request

class KtronixScrapingSpider(Spider):
	name = 'ktronix_scraping'
	allowed_domains = ['ktronix.com']
	start_urls = ['http://ktronix.com/']

	def parse(self, response):

		try: n_cat = response.meta['n_cat']
		except: n_cat = 0 

		print('\n','#'*20, 'Este es n_cat !!', '\n', n_cat)

		categories =  response.xpath('//*[@class= "outer_ele"]/div/a/@href').extract()

		print(categories)

		category = categories[n_cat] 



		yield Request(url= category,
					  callback= self.category_parse,
					  meta= {'n_cat': n_cat,
							 'categories': categories,
							 'category': category},
					  dont_filter= True)



	def category_parse(self, response):
		n_cat = response.meta['n_cat']
		categories = response.meta['categories']
		category = response.meta['category']

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
			except IndexError:
				disc_price = 0

			except:
				disc_price = disc_price =product.xpath('.//*[@class= "price-box"]/span[@class= "regular-price"]//text()').extract()
				if disc_price != []:
					disc_price =product.xpath('.//*[@class= "price-box"]/span[@class= "regular-price"]//text()').extract()[2]
				else:
					disc_price = 0
			
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
								'pag': pag},
						dont_filter= True)


		elif n_cat < len(categories) - 1:
			n_cat += 1
			yield Request(url= 'http://ktronix.com/',
						  callback= self.parse,
						  dont_filter= True,
						  meta= {'n_cat': n_cat}) 

		else:
			print('\n', '='*20,'\n', 'TAL PARECE QUE SE EXTRAJO TODA LA INFORMACION DE LA PAGINA !!','\n', '='*20, '\n')