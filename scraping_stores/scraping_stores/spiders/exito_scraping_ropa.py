from scrapy import Spider
from scrapy.http import Request
from scrapy.selector import Selector

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import os

from requests import get
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


def download_image(img_url, filename, path):
	try: os.mkdir(path)
	except: pass

	with open(path + filename, 'wb') as image:

		check_connection()
		image.write(get(img_url).content)

# def wait_time()

def ext_func(prod_variable):
	if '?' in prod_variable:
		return '&'
	else:
		return '?'


# self.driver = webdriver.Firefox()
# self.driver.maximize_window()
# sleep(10)
# self.driver.set_page_load_timeout(45)


check_connection()


class ExitoScrapingRopaSpider(Spider):
	name = 'exito_scraping_ropa'
	allowed_domains = ['exito.com']
	start_urls = ['http://www.exito.com/category']

	def start_request(self):
		for url in start_urls:

			check_connection()
			yield Request(url = url + '/category',
						  callback = self.parse)


	def parse(self, response):

		self.driver = webdriver.Firefox()
		self.driver.maximize_window()
		sleep(10)
		self.driver.set_page_load_timeout(45)


		print('\n', '*'*40, '\n')
		print(response.meta)
		print('\n', '*'*40, '\n')

		try: n_cat = response.meta['n_cat']
		except: n_cat = 0 ###################################################### OJO !!

		print('\n', '*'*40, '\n', response.status)
		print(response.url)
		print('\n', '*'*40, '\n')

		categories = response.xpath('//*[@class = "fl w-30"]//a/@href').extract()

		categories = [url for url in categories if 'moda' in url]

		print(categories)

		category = categories[n_cat]

		if 'deportes' in category:
			category = category.split('-tiempo')[0]			

		check_connection()
		yield Request(url = 'https://www.exito.com' + category,
					  callback = self.prod_parse,
					  meta = {'category': category,
							  'n_cat': n_cat,
							  'categories': categories})


	def prod_parse(self, response):
		n_cat = response.meta['n_cat']
		categories = response.meta['categories']
		category = response.meta['category']

		print('\n', '*'*40, '\n', response.status)
		print(response.url)
		print('\n', '*'*40, '\n')

		prod_types = []

		if 'mercado' in category:
			prod_types = response.xpath('//*[@class = "exito-home-components-1-x-containerCarouselGrid"]/a/@href').extract()[2:]
		



		elif 'salud' in category or 'deportes' in category:
			trys_cat = 1
			while trys_cat <= 5:
				try:
					check_connection()
					self.driver.get(response.url)
					break
				except:
					trys_cat += 1

			prod_types = Selector(text= self.driver.page_source)
			prod_types = prod_types.xpath('//*[@class= "diagramacion-outfit w-100 flex-m flex-column-s flex-row-l "]//a/@href').extract()
			prod_types = [x.split('https://www.exito.com')[-1] for x in prod_types]		



		elif 'moda' in category:

			trys_cat = 1
			while trys_cat <= 5:
				try:
					check_connection()
					self.driver.get(response.url)
					break
				except:
					trys_cat += 1
			
			page_body = Selector(text= self.driver.page_source)

			list_1 = page_body.xpath('//*[@class= "diagramacion-outfit w-100 flex-m flex-column-s flex-row-l "]//a/@href').extract()
			list_2 = page_body.xpath('//*[@class= "pt5-l pt1-s w-100 flex-wrap-s flex-nowrap-l diagramacion-outfit flex justify-between  "]//a/@href').extract()
			
			list_3 = page_body.xpath('//*[@class= "exito-home-components-1-x-carouselByScroll flex"]')[1:]
			list_3 =  list_3.xpath('.//a/@href').extract()

			prod_types = 	prod_types + list_1 + list_2 + list_3 




		else:
			trys_cat = 1
			while trys_cat <= 5:
				try:
					check_connection()
					self.driver.get(response.url)
					break
				except:
					trys_cat += 1
			sleep(10)
			prod_types = Selector(text= self.driver.page_source)
			prod_types = prod_types.xpath('.//*[@class = "exito-home-components-1-x-carouselByScroll flex"]/a/@href').extract()
			prod_types = [x.split('https://www.exito.com')[-1] for x in prod_types]
			# print(prod_types)
		
		for prod_type in prod_types:
			cache = {'cat_name': ['NA']}
			if 'comida' not in prod_type:
				
				pag = 1
				exten = ext_func(prod_type)

				if '&page' in prod_type:
					prod_type = prod_type.split('&page')[0]

				while True:
					url_cat_pag = 'https://www.exito.com' + prod_type + exten + 'page=' + str(pag)

					trys_prod = 1
					while trys_prod <= 5:
						try:
							print('\n', '#'*15, 'Intento numero ', trys_prod, '#'*15, '\n') 
							check_connection()
							self.driver.get(url_cat_pag)
							break
						except:
							print('\n', '#'*15, 'Fallo intento', '#'*15, '\n')
							trys_prod +=1
							
					pag_sel = Selector(text= self.driver.page_source)
					
					print('Antes de dormir')
					sleep(15)
					self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
					print('Despues de dormir')
					sleep(5)
					cat_name = pag_sel.xpath('.//*[@class= "vtex-breadcrumb-1-x-container pv3"]/span/a/text()').extract()
					
					print('$'*40)
					print(cat_name)
					print('$'*40)
					
					pag_sel = Selector(text= self.driver.page_source)
					sig = pag_sel.xpath('.//*[@class= "vtex-button__label flex items-center justify-center h-100 ph5 "]')

					print('$'*40)
					print('\t\t' 'RESULTADO SI EL BOTON ESTA', sig)
					print('$'*40)
					
					if sig != []:
						print('########################################## entro al IF #################################################')	
						productos = pag_sel.xpath('.//*[@class= "vtex-search-result-3-x-galleryItem vtex-search-result-3-x-galleryItem--normal pa4"]')
						
						print('$'*40)
						print('\t\t' 'RESULTADO DE PRODUCTOS ENCONTRADOS \n', len(productos))
						print('$'*40)

						for producto in productos: 
							try:
								prod_name = producto.xpath('.//*[@class= "vtex-store-components-3-x-productNameContainer mv0 test"]/span/text()').extract_first()
								prod_name = prod_name.replace('\\', '.')
								prod_name = prod_name.replace('/', '.')

								if prod_name != None or prod_name != []:
									prod_name = prod_name.strip() 

								normal_price = producto.xpath('.//*[@style= "display: initial;"]//span/text()').extract()



								try:
									button = self.driver.find_element_by_css_selector('.exito-geolocation-3-x-primaryButton')
								except:
									button = []
								
								print(normal_price, '------')

								if normal_price != [] and button == []:
									if normal_price[-1] == 'otros':
										normal_price = producto.xpath('.//*[@style= "display: initial;"]//span/text()').extract()[0]
										disc_price = producto.xpath('.//*[@style= "display: initial;"]//span/text()').extract()[-2]
									else:
										normal_price = producto.xpath('.//*[@style= "display: initial;"]//span/text()').extract()[0]
										disc_price = producto.xpath('.//*[@style= "display: initial;"]//span/text()').extract()[-1]

								elif button != []:
									raise IndexError()
								else:
									normal_price = 0
									disc_price = 0
								image_url = producto.xpath('.//*[@class= "vtex-product-summary-2-x-imageNormal vtex-product-summary-2-x-image"]/@src').extract_first()
							
							except:
								self.driver.find_element_by_css_selector('.exito-autocomplete-3').click()
								self.driver.find_element_by_css_selector('#react-select-2-input').send_keys('Bogotá')
								self.driver.find_element_by_css_selector('#react-select-2-input').send_keys(Keys.ENTER)
								self.driver.find_element_by_css_selector('.exito-geolocation-3-x-primaryButton').click()
								sleep(15)
								break


							print('\n', '#'*50, 'Estamos en la pagina ', pag, '#'*50, '\n')
							print('\nCategoria:\t', cat_name,
								  '\n\tProducto:\t', prod_name,
								  '\n\tNormal price:\t', normal_price,
								  '\n\tDiscount price:\t', disc_price)


							if cat_name != [] and type(cat_name) == list:
								cat_name = cat_name[-1]

							elif type(cat_name) == str:
								cat_name = cat_name
							else :
								cat_name = cache['cat_name'][0]

							# filename = prod_name + '.jpg'
							# path = './resultados/mercado/' + cat_name + '/'
							# cache['cat_name'] = [cat_name]
							# download_image(image_url, filename, path)

							yield {'cat_name': cat_name,
								   'prod_name': prod_name,
								   'normal_price': normal_price,
								   'disc_price': disc_price,
								   'image_url': image_url}

							print('#'*80)

						if 'chaquetas&map' not in prod_type and 'zromanella?' not in prod_type:
							pag += 1
						else:
							break
					
					else:
						print('################################ Entra al else #################################')
						break
				print('='*100)
				#break
		print('\n', '/'*20, 'Antes del IF para pasar de categoria', '/'*20, '\n')
		n_cat += 1
		if n_cat < len(categories):
			print('/'*20, 'Dentro del IF para pasar de categoria', '/'*20, '\n')
			
			check_connection()
			yield Request(url = 'https://www.exito.com/category',
						  callback = self.parse,
						  meta = {'n_cat': n_cat},
						  dont_filter = True)
		
		else:
			print('SE HA TERMINADO DE EXTRAER INFO DE LA PAGINA !!')			
