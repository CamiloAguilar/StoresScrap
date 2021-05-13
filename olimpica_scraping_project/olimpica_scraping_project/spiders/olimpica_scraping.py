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


def url_part(url):
	if 'supermercado' in url:
		return '&page='
	else:
		return '?page='

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

		try: categories = response.meta['categories']
		except: pass 
		
		try: n_cat = response.meta['n_cat']
		except: n_cat = 0 ##################################################### OJO !!

		if n_cat == 0:
			driver.get('https://www.olimpica.com/')
			sleep(10)

			driver.find_element_by_xpath('//*[@class=" vtex-store-drawer-0-x-menuIcon"]').click()
			sleep(3)
			
			categories_page_sel = Selector(text= driver.page_source)
			categories = categories_page_sel.xpath('//*[@class= "olimpica-mega-menu-0-x-Level1Container"]//a/@href').extract()

			category = categories[n_cat]
			driver.get('https://www.olimpica.com' + category)
			sleep(10)

			supermecado_cats_sel = Selector(text= driver.page_source)
			supermecado_cats = supermecado_cats_sel.xpath('//*[@class="flex mt0 mb0 pt0 pb0    justify-start  vtex-flex-layout-0-x-flexRowContent vtex-flex-layout-0-x-flexRowContent--landing-app-section vtex-flex-layout-0-x-flexRowContent--landing-app-section-variety items-stretch w-100"]//a/@href').extract()
			supermecado_cats = list(dict.fromkeys(supermecado_cats))

			categories = supermecado_cats + categories


		category = categories[n_cat]

		print()
		print(categories)
		print()
		
		# import pdb; pdb.set_trace()

		check_connection()
		yield Request(url= 'http://olimpica.com' + category,
					 callback= self.category_parse,
					 meta= {'n_cat': n_cat,
							'categories': categories})



	def category_parse(self, response):
		n_cat = response.meta['n_cat']
		categories = response.meta['categories']
		pag = 1

		parte = url_part(response.url)


		while True:

			print('\n', response.url + parte + str(pag), '\n')

			check_connection()
			driver.get(response.url + parte + str(pag))
			sleep(3)

			driver.execute_script('document.body.style.MozTransform = "scale(0.2)";')
			sleep(.5)
			driver.execute_script('document.body.style.MozTransformOrigin = "0 0";')
			sleep(1)


			button_test_trys = 0
			button_bool = False
			while button_test_trys <= 20:
				cat_page_sel = Selector(text= driver.page_source)
				button_test = cat_page_sel.xpath('//*[@class="vtex-button bw1 ba fw5 v-mid relative pa0 lh-solid br2 min-h-small t-action--small bg-action-primary b--action-primary c-on-action-primary hover-bg-action-primary hover-b--action-primary hover-c-on-action-primary pointer "]')
				if button_test != []:
					button_bool = True
					break
				else:
					button_test_trys += 1
					sleep(2)

			if button_bool:

				ver_mas_prods = 0
				while ver_mas_prods < 10:
					cat_page_sel = Selector(text= driver.page_source)
					n_prods = len(cat_page_sel.xpath('//*[@class= "vtex-flex-layout-0-x-flexColChild vtex-flex-layout-0-x-flexColChild--search-result-content pb0"]//*[@class="vtex-search-result-3-x-galleryItem vtex-search-result-3-x-galleryItem--normal vtex-search-result-3-x-galleryItem--grid-3 pa4"]'))

					if n_prods != 0 and n_prods >= 11:
						break

					else:
						ver_mas_prods += 1
						driver.execute_script("window.scrollTo(0, window.scrollY + 3)")
						sleep(1)
						driver.execute_script("window.scrollTo(0, window.scrollY - 3)")
						sleep(1)


				driver.execute_script('document.body.style.MozTransform = "scale(0.005)";')
				driver.execute_script('document.body.style.MozTransformOrigin = "0 0";'	)


				sleep(2)

				#import pdb; pdb.set_trace()

				cat_page_sel = Selector(text= driver.page_source)
				n_prods = len(cat_page_sel.xpath('//*[@class= "vtex-flex-layout-0-x-flexColChild vtex-flex-layout-0-x-flexColChild--search-result-content pb0"]//*[@class="vtex-search-result-3-x-galleryItem vtex-search-result-3-x-galleryItem--normal vtex-search-result-3-x-galleryItem--grid-3 pa4"]'))

				prods = cat_page_sel.xpath('//*[@class= "vtex-flex-layout-0-x-flexColChild vtex-flex-layout-0-x-flexColChild--search-result-content pb0"]//*[@class="vtex-search-result-3-x-galleryItem vtex-search-result-3-x-galleryItem--normal vtex-search-result-3-x-galleryItem--grid-3 pa4"]')

				cat_name = cat_page_sel.xpath('.//*[@class= "vtex-search-result-3-x-galleryTitle--layout t-heading-1"]//text()').extract()[-1]

				for prod in prods:
					prod_name = prod.xpath('.//*[@class= "vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body"]//text()').extract_first()
					
					normal_price = prod.xpath('.//*[@class= "vtex-product-price-1-x-listPriceValue vtex-product-price-1-x-listPriceValue--summary strike"]//text()').extract()

					if normal_price == []:
						normal_price = prod.xpath('.//*[@class= "vtex-product-price-1-x-sellingPriceValue vtex-product-price-1-x-sellingPriceValue--summary"]//text()').extract()


					if normal_price != []:
						normal_price = ' '.join(normal_price)

					disc_price = prod.xpath('.//*[@class= "vtex-product-price-1-x-currencyContainer vtex-product-price-1-x-currencyContainer--summary"]//text()').extract()
					if disc_price != []:
						disc_price = ' '.join(disc_price)			


					image_url = prod.xpath('.//*[@class= "vtex-product-summary-2-x-imageNormal vtex-product-summary-2-x-image"]/@src').extract_first()

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

				pag += 1
				continue

			else:
				break

		print('\n', 'Se econtraron en total', n_prods)

		# import pdb; pdb.set_trace()

		if n_cat < len(categories)-1:
			n_cat +=1

			check_connection()
			yield Request(url= 'http://olimpica.com/',
						  callback= self.parse,
						  meta= {'n_cat': n_cat, 'categories': categories},
						  dont_filter= True)

		else:
			driver.quit()


