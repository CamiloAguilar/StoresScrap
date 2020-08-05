from scrapy import Spider
from scrapy.http import Request

from selenium import webdriver
from scrapy.selector import Selector
from selenium.common.exceptions import ElementClickInterceptedException

from time import sleep


options = webdriver.FirefoxOptions()
options.add_argument('--headless')
driver = webdriver.Firefox(options = options)

#driver = webdriver.Firefox()


class AlkostoScrapingSpider(Spider):
	name = 'alkosto_scraping'
	allowed_domains = ['alkosto.com']
	start_urls = ['http://alkosto.com/']


	def parse(self, response):

		try: n_cat = response.meta['n_cat']
		except: n_cat = 14 ###################################################################### OJO !!

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
			print('\n',response.url)
			mercado_link = response.xpath('//*[@class= "btn-ver-mas center"]/@href').extract_first()
			
			yield Request(url = mercado_link,
						  callback= self.mercado_parse)



	def mercado_parse(self, response):
		print('entro en el parse para mercado')
		print('\n', response.url)

		try: mercado_n_cat = response.meta['mercado_n_cat']
		except: mercado_n_cat = 0
		trys = 1

		while trys <= 5:
			try:
				print('\n','*'*10, 'INTENTO # ', trys,'*'*10, '\n')
				driver.get(response.url)
				if trys <= 3:
					sleep(3)
				else:
					sleep(5)

				buttons = driver.find_elements_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div')

				buttons[mercado_n_cat].click()
				break
			except:
				trys +=1

		sleep(3)
		pag = 1
		while True:
			print('\n', '#'*15, 'Estamos en la pagina ', pag,'#'*15, '\n')
			mercado_pag_sel = Selector(text= driver.page_source)
			mercado_products = mercado_pag_sel.xpath('.//*[@class= "ProductDisplay-sc-5nadct-0 ldPWHL"]/div')

			cat_name = mercado_pag_sel.xpath('//h1/text()').extract_first()
			print('\n', '#'*15, 'De la categoria ', cat_name,'#'*15, '\n')
			print('Vamos en la categoria n ', mercado_n_cat+1, len(buttons))
			sleep(3)

			try:
				for mercado_product in mercado_products:

					prod_name = mercado_product.xpath('.//*[@class= "product__content__name"]//text()').extract_first()
					disc_price = mercado_product.xpath('.//*[@class= "product__content__price__wrapper"]/p/text()').extract()
					
					print(disc_price, 'este es disc_price de largo', len(disc_price))

					if len(disc_price) > 1:
						print('ESTE ENTRA AL IF')
						normal_price = disc_price[-1]
						disc_price = disc_price[1]
					
					else:
						print('ESTE ENTRA AL ELSE')
						normal_price = disc_price[0]
						disc_price = disc_price[0]
					
					image_url = mercado_product.xpath('.//*[@class= "product__figure-wrapper__img"]/@src').extract_first()

					print('\n', '#'*15, 'Resultado Producto', '#'*15, '\n')
					print('Categoria: ', cat_name, '\n',
						  '\n\tProducto:\t', prod_name,
						  '\n\tPrecio norm:\t', normal_price,
						  '\n\tPrecio desc:\t', disc_price, '\n')
					

				
					yield {'cat_name': cat_name,
						   'prod_name': prod_name,
						   'normal_price': normal_price,
						   'disc_price': disc_price,
						   'image_url': image_url}

				
				next_button= driver.find_elements_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/ul/li/a')
				if next_button != []:
					#next_button= driver.find_elements_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/ul/li/a')[-1].click()
					next_button[-1].click()
					sleep(3)
				else:
					raise ElementClickInterceptedException()
				pag += 1


			except ElementClickInterceptedException:

				if mercado_n_cat < len(buttons)-1:

					mercado_n_cat += 1
					yield Request(url = response.url,
								  callback= self.mercado_parse,
								  meta= {'mercado_n_cat': mercado_n_cat},
								  dont_filter= True)
					break
					
				
				else:
					print('\n', '='*20,'\n', 'TAL PARECE QUE SE EXTRAJO TODA LA INFORMACION DE LA PAGINA !!','\n', '='*20, '\n')
					driver.quit()
					break
