from scrapy import Spider
from scrapy.http import Request
from scrapy.selector import Selector

from selenium import webdriver

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




# options = webdriver.FirefoxOptions()
# options.add_argument('--headless')
# driver = webdriver.Firefox(options = options)

driver = webdriver.Firefox()
#driver.execute_script("document.body.style.transform = 'scale(1)'")

check_connection()

class OlimpicaScrapingSpider(Spider):
	name = 'olimpica_scraping'
	allowed_domains = ['olimpica.com']
	start_urls = ['http://olimpica.com/']

	def parse(self, response):

		try: n_cat = response.meta['n_cat']
		except: n_cat = 0

		categories = response.xpath('//*[@class= "menu"]/li[@class= "item-submenu"]/a/@href').extract()

		category = categories[n_cat]

		check_connection()
		yield Request(url= 'http://olimpica.com' + category,
					 callback= self.category_parse,
					 meta= {'n_cat': n_cat,
							'categories': categories})

	def category_parse(self, response):
		n_cat = response.meta['n_cat']
		categories = response.meta['categories']

		print('\n', response.url, '\n')

		check_connection()
		driver.get(response.url)
		sleep(3)

		cat_page_sel = Selector(text= driver.page_source)

		n_prods = len(cat_page_sel.xpath('//*[@class= "product-list n1colunas"]/ul'))

		while True:
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			sleep(5)
			cat_page_sel = Selector(text= driver.page_source)
			n_prods_test = len(cat_page_sel.xpath('//*[@class= "product-list n1colunas"]/ul'))
			if n_prods == n_prods_test:
				break
			else:
				n_prods = n_prods_test

		cat_page_sel = Selector(text= driver.page_source)
		n_prods = len(cat_page_sel.xpath('//*[@class= "product-list n1colunas"]/ul'))

		prods = cat_page_sel.xpath('.//*[@class= "product-list n1colunas"]/ul')

		cat_name = cat_page_sel.xpath('.//*[@class= "bread-crumb"]/ul/li//text()').extract()[-1]

		for prod in prods:
			prod_name = prod.xpath('.//*[@class= "data"]/a[@class= "product-name"]/text()').extract_first()
			
			normal_price = prod.xpath('.//*[@class= "data"]/div[@class= "product-price"]/span/text()').extract()

			if len(normal_price) > 1:
				disc_price = normal_price[-1]
				normal_price = normal_price[0]

			elif len(normal_price) == 1:
				disc_price = normal_price[0]
				normal_price = normal_price[0]
			
			else:
				disc_price = 0
				normal_price = 0

			image_url = prod.xpath('.//a[@class= "imagen-prod"]//@src').extract_first()

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

		print('\n', 'Se econtraron en total', n_prods)



		if n_cat < len(categories)-1:
			n_cat +=1

			check_connection()
			yield Request(url= 'http://olimpica.com/',
						  callback= self.parse,
						  meta= {'n_cat': n_cat},
						  dont_filter= True)

		else:
			driver.quit()


