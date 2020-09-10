from scrapy import Spider
from scrapy.http import Request
from scrapy.selector import Selector


from selenium import webdriver

from time import sleep
from datetime import date




def ext_func(prod_variable):
	if '?' in prod_variable:
		return '&'
	else:
		return '?'



def next_button_func(button_list):
	test = []

	for button in button_list:
		if 'Mostrar más' in button:
			test.append(True)
		else:
			test.append(False)

	return sum(test)






class ColsubsidioScrapingSpider(Spider):
	name = 'colsubsidio_scraping'


	custom_settings = {
						'FEED_FORMAT': "csv",
						'FEED_URI': './resultados/supermercado_data/supermercado_data_date_' + str(date.today()) + '.csv',
						'FEED_EXPORTERS': {
								'csv': 'scrapy.exporters.CsvItemExporter'
							},
						'FEED_EXPORT_ENCODING': 'utf-8',
 						}


	allowed_domains = ['supermercadoscolsubsidio.com']
	start_urls = ['https://www.supermercadoscolsubsidio.com/']


	


	def parse(self, response):

		self.driver = webdriver.Firefox()
		sleep(5)

		print()
		print(response.url)
		print()

		yield Request(url= response.url,
					  callback= self.supermercado_parse)


	def supermercado_parse(self, response):
		print()
		print(response.url, '------------------------> supermercado')
		print()

		n_cat = 0 ############################################################# OJO !!

		self.driver.get(response.url)
		sleep(3)
		self.driver.execute_script("window.scrollTo(0, window.scrollY + 10)")

		print('Antes del click')
		while True:
			self.driver.find_element_by_css_selector('.vtex-flex-layout-0-x-flexColChild--search-out-categories-right-container > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > section:nth-child(1) > button:nth-child(2)').click()
			
			main_page_sel = Selector(text= self.driver.page_source)
			categories = main_page_sel.xpath('//*[@class= "vtex-store-components-3-x-imageElementLink"]/@href').extract()
			if len(categories) > 7:
				break 

		main_page_sel = Selector(text= self.driver.page_source)
		categories = main_page_sel.xpath('//*[@class= "vtex-store-components-3-x-imageElementLink"]/@href').extract()
		otro_url = main_page_sel.xpath('//*[@class= "vtex-slider-layout-0-x-imageElementLink vtex-slider-layout-0-x-imageElementLink--main-carousel vtex-store-components-3-x-imageElementLink vtex-store-components-3-x-imageElementLink--main-carousel"]/@href').extract()
		categories = list(dict.fromkeys(categories + otro_url)) ################# OJO !!

		#categories = otro_url

		# self.driver.quit() ##################################### OJO !!

		yield Request(url = response.url,
					  callback= self.parse_ini,
					  meta= {'n_cat': n_cat,
							 'categories':categories},
					  dont_filter= True)


	def parse_ini(self, response):
		n_cat = response.meta['n_cat']
		categories = response.meta['categories']
		pag = 1

		trys = 1

		category = categories[n_cat]

		exten = ext_func(category)

		yield Request(url= 'https://www.supermercadoscolsubsidio.com' + category + exten + 'page='+ str(pag),
					  callback= self.main_mercado,
					  meta = {'n_cat': n_cat,
							  'categories':categories,
							  'category': category,
							  'pag': pag,
							  'exten': exten,
							  'trys': trys})


	def main_mercado(self, response):
		print()
		print('*'*15, 'estamos en la pag', '*'*15)
		print(response.url)
		print()
		print(response.status)
		print()


		n_cat = response.meta['n_cat']
		categories = response.meta['categories']
		pag = response.meta['pag']
		category = response.meta['category']
		exten = response.meta['exten']
		trys = response.meta['trys']

		prods = response.xpath('//*[@class= "vtex-search-result-3-x-gallery flex flex-row flex-wrap items-stretch bn ph1 na4 pl9-l"]/div')



		cat_name= response.xpath('//*[@class= "vtex-search-result-3-x-galleryTitle--layout t-heading-1"]/text()').extract_first()

		button_next = response.xpath('//*[@class= "vtex-button__label flex items-center justify-center h-100 ph5 "]/text()').extract()

		if '.com/26' in response.url:
			self.driver.get(response.url)
			sleep(3)
			self.driver.execute_script('document.body.style.MozTransform = "scale(0.3)";')
			self.driver.execute_script('document.body.style.MozTransformOrigin = "0 0";')
			self.driver.execute_script("window.scrollTo(0, window.scrollY + 3)")
			sleep(5)

			cat_page_sel = Selector(text= self.driver.page_source)

			prods = cat_page_sel.xpath('//*[@class= "vtex-search-result-3-x-gallery flex flex-row flex-wrap items-stretch bn ph1 na4 pl9-l"]/div')
			cat_name= cat_page_sel.xpath('//*[@class= "vtex-search-result-3-x-galleryTitle--layout t-heading-1"]/text()').extract_first()

			button_next = cat_page_sel.xpath('//*[@class= "vtex-button__label flex items-center justify-center h-100 ph5 "]/text()').extract()



		for prod in prods:
			prod_name = prod.xpath('.//*[@class= "vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body"]/text()').extract_first()

			normal_price = prod.xpath('.//*[@class= "flex mt0 mb0 pt0 pb0    justify-start  vtex-flex-layout-0-x-flexRowContent items-stretch w-100"]/div/span//text()').extract() 

			if normal_price != []:
				disc_price = normal_price[0]
				normal_price = normal_price[-1]
			else:
				disc_price = 0
				normal_price = 0 


			image_url= prod.xpath('.//*[@class= "vtex-product-summary-2-x-imageNormal vtex-product-summary-2-x-image"]/@src').extract_first()


			print('\n', '#'*50, 'Estamos en la pagina ', pag, '#'*50, '\n')
			print('\nCategoria:\t', cat_name,
				  '\n\tProducto:\t', prod_name,
				  '\n\tNormal price:\t', normal_price,
				  '\n\tDiscount price:\t', disc_price, '\n')


			yield {'cat_name': cat_name,
				   'prod_name': prod_name,
				   'normal_price': normal_price,
				   'disc_price': disc_price,
				   'image_url': image_url}


		
		test = next_button_func(button_next)


		if prods == [] and trys <= 10:
			trys += 1

			yield Request(url= response.url,
						  callback= self.main_mercado,
						  meta = {'n_cat': n_cat,
								  'categories':categories,
								  'category': category,
								  'pag': pag,
								  'exten': exten,
							  	  'trys': trys},
						  dont_filter= True)

		elif test > 0:
			pag += 1
			trys = 1
			yield Request(url= 'https://www.supermercadoscolsubsidio.com' + category + exten + 'page='+ str(pag),
						  callback= self.main_mercado,
						  meta = {'n_cat': n_cat,
								  'categories':categories,
								  'category': category,
								  'pag': pag,
								  'exten': exten,
							  	  'trys': trys})




		elif n_cat < len(categories)-1:
			sleep(15)
			n_cat += 1

			yield Request(url = response.url,
						  callback= self.parse_ini,
						  meta= {'n_cat': n_cat,
								 'categories':categories},
						  dont_filter= True)

		else:
			self.driver.quit()
			print('SE HA TERMINADO DE EXTRAER INFO DE LA PAGINA !!')









