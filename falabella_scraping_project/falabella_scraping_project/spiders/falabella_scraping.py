from scrapy import Spider
from scrapy.http import Request
from scrapy.selector import Selector

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException


from time import sleep



driver = webdriver.Firefox()
driver.maximize_window()
sleep(10)
driver.set_page_load_timeout(45)



def unic_func(url_list):
	new_url_list = []
	for url in url_list:
		
		if '/falabella-co/' not in url:
			url = '/falabella-co/' + url
			new_url_list.append(url)
	
		elif 'https://www.falabella.com.co' in url:
			url = url.split('https://www.falabella.com.co')[-1]
			new_url_list.append(url)

		else:
			new_url_list.append(url)

	return new_url_list




class FalabellaScrapingSpider(Spider):
	name = 'falabella_scraping'
	allowed_domains = ['falabella.com.co']
	start_urls = ['http://falabella.com.co/']


	def parse(self, response):

		n_cat = 60 ########################################################################################## ojo !
		print('\n')
		print(response.url)
		print('\n')
		driver.get(response.url)
		
		main_page_source = Selector(text= driver.page_source)
		
		gen_categories = main_page_source.xpath('.//*[@class= "ThirdLevelItems_submenuElementLiBold__1aiT_"]/@href').extract()
		
		gen_categories = unic_func(gen_categories)
		gen_categories = list(dict.fromkeys(gen_categories))

		categories = []
		for cate in gen_categories:
			#print(cate, '----->', cate.count('?isPLP=1'))
			if cate.count('?isPLP=1') == 2:
				cate = cate.replace('?isPLP=1', '', 1)
				#print(cate, '----->', cate.count('?isPLP=1'), '\n')
				categories.append(cate)
			elif cate.count('?isPLP=1') == 3:
				cate = cate.replace('?isPLP=1', '', 2)
				#print(cate, '----->', cate.count('?isPLP=1'), '\n')
				categories.append(cate)
			else:
				#print(cate, '----->', cate.count('?isPLP=1'), '\n')
				categories.append(cate)
		print(categories)


		#sleep(60)

		
		yield Request(url= response.url,
					  callback= self.first_parse_cats,
					  meta= {'n_cat': n_cat,
							 'categories': categories})
		



	def first_parse_cats(self, response):
		
		categories = response.meta['categories']
		n_cat = response.meta['n_cat']
		
		category = categories[n_cat]
		
		yield Request(url= 'https://www.falabella.com.co' + category,
					  callback= self.main_parse_cats,
					  meta= {'n_cat': n_cat, 'categories': categories})
		




	def main_parse_cats(self, response):
		
		global driver
		try:
			categories = response.meta['categories']
			n_cat = response.meta['n_cat']

			trys= 1

			while trys <= 3:
				try:
					print('\n', '#'*15,'Estamos en el intento', trys, '#'*15, '\n') 
					driver.get(response.url)
					break
				except:
					print('FALLO INTENTO')
					trys += 1

			sleep(3)
			

			pag = 1

			while True:
				cache_url = driver.current_url

				print('\n', cache_url, '----------> Este es el cache url', '\n')

				try:
					driver.execute_script('document.body.style.MozTransform = "scale(0.3)";')
					driver.execute_script('document.body.style.MozTransformOrigin = "0 0";')
					driver.execute_script("window.scrollTo(0, window.scrollY - 10000)")
				except:
					driver.refresh()
					sleep(5)
					driver.execute_script('document.body.style.MozTransform = "scale(0.3)";')
					driver.execute_script('document.body.style.MozTransformOrigin = "0 0";')
					driver.execute_script("window.scrollTo(0, window.scrollY - 10000)")

				sleep(1.5)

				for scroll in range(3):

					if scroll == 0:
						driver.execute_script("window.scrollTo(0, window.scrollY + 300)")
						sleep(1)
					else:
						driver.execute_script("window.scrollTo(0, window.scrollY + 635)")
						sleep(1)

				categ_prods_page = Selector(text= driver.page_source)
				prods = categ_prods_page.xpath('//*[@id= "testId-searchResults-products"]/div')
				
				cat_name = categ_prods_page.xpath('.//*[@class= "jsx-1134953126 brand-title-container collection-title"]//text()').extract_first()

				if cat_name == None:
					cat_name = categ_prods_page.xpath('.//*[@class= "jsx-3139645404 categoty-title-container"]/span//text()').extract_first()

				try:
					for prod in prods:

						prod_name = prod.xpath('.//b[@class= "jsx-3773340100 copy2 primary  jsx-185326735 normal    pod-subTitle"]/text()').extract_first()

						if prod_name == None:
							prod_name = prod.xpath('.//b[@class= "jsx-287641535 title2 primary  jsx-185326735 bold    pod-subTitle"]/text()').extract_first()

						if prod_name == None:
							prod_name = prod.xpath('.//b[@class= "jsx-3773340100 copy13 primary  jsx-185326735 normal    pod-subTitle"]/text()').extract_first()

						print(prod_name, '---------> prod name')

						normal_price= prod.xpath('.//ol/li//span/text()').extract()
						normal_price= [price for price in normal_price if '$' in price]

						disc_price = normal_price[0]
						normal_price = normal_price[-1]

						image_url = prod.xpath('.//img/@src').extract_first()

						print('\n', '#'*50, 'Estamos en la pagina ', pag, '#'*50, '\n')
						print('\nCategoria:\t', cat_name,
							  '\n\tProducto:\t', prod_name,
							  '\n\tNormal price:\t', normal_price,
							  '\n\tDiscount price:\t', disc_price)


						yield {'cat_name': cat_name,
							   'prod_name': prod_name,
							   'normal_price': normal_price,
							   'disc_price': disc_price,
							   'image_url': image_url}

					print('Antes del click')
					driver.find_element_by_css_selector('#testId-pagination-top-arrow-right').click()
					print('Despues del click')  
					
					pag += 1

				except NoSuchElementException:
					break

				except TimeoutException:
					trys2 = 1

					while trys2 <= 3:
						try:
							print('\n', '#'*15,'FALLO EL CLICK, ¡ COMENZAMOS !', '#'*15, '\n') 
							driver.refresh()
							break
							
						except:
							print('FALLO INTENTO DEL CLICK')
							trys2 += 1

					continue


		except WebDriverException:
			print('Entra al except de la excepcion que es !! ---------------------------------')

			driver = webdriver.Firefox()
			driver.maximize_window()
			sleep(10)
			driver.set_page_load_timeout(45)

			driver.get(cache_url)
			sleep(10)



			pag = 1

			while True:
				cache_url = driver.current_url


				print('\n', cache_url, '----------> Este es el cache url', '\n')

				try:    
					driver.execute_script('document.body.style.MozTransform = "scale(0.3)";')
					driver.execute_script('document.body.style.MozTransformOrigin = "0 0";')
					driver.execute_script("window.scrollTo(0, window.scrollY - 10000)")
				except:
					driver.refresh()
					sleep(5)
					driver.execute_script('document.body.style.MozTransform = "scale(0.3)";')
					driver.execute_script('document.body.style.MozTransformOrigin = "0 0";')
					driver.execute_script("window.scrollTo(0, window.scrollY - 10000)")

				sleep(1.5)

				for scroll in range(3):

					if scroll == 0:
						driver.execute_script("window.scrollTo(0, window.scrollY + 300)")
						sleep(1)
					else:
						driver.execute_script("window.scrollTo(0, window.scrollY + 635)")
						sleep(1)

				categ_prods_page = Selector(text= driver.page_source)
				prods = categ_prods_page.xpath('//*[@id= "testId-searchResults-products"]/div')
				
				cat_name = categ_prods_page.xpath('.//*[@class= "jsx-1134953126 brand-title-container collection-title"]//text()').extract_first()

				if cat_name == None:
					cat_name = categ_prods_page.xpath('.//*[@class= "jsx-3139645404 categoty-title-container"]/span//text()').extract_first()

				try:
					for prod in prods:

						prod_name = prod.xpath('.//b[@class= "jsx-3773340100 copy2 primary  jsx-185326735 normal    pod-subTitle"]/text()').extract_first()

						if prod_name == None:
							prod_name = prod.xpath('.//b[@class= "jsx-287641535 title2 primary  jsx-185326735 bold    pod-subTitle"]/text()').extract_first()

						print(prod_name, '---------> prod name')

						normal_price= prod.xpath('.//ol/li//span/text()').extract()
						normal_price= [price for price in normal_price if '$' in price]

						disc_price = normal_price[0]
						normal_price = normal_price[-1]

						image_url = prod.xpath('.//img/@src').extract_first()

						print('\n', '#'*50, 'Estamos en la pagina ', pag, '#'*50, '\n')
						print('\nCategoria:\t', cat_name,
							  '\n\tProducto:\t', prod_name,
							  '\n\tNormal price:\t', normal_price,
							  '\n\tDiscount price:\t', disc_price)


						yield {'cat_name': cat_name,
							   'prod_name': prod_name,
							   'normal_price': normal_price,
							   'disc_price': disc_price,
							   'image_url': image_url}

					print('Antes del click')
					driver.find_element_by_css_selector('#testId-pagination-top-arrow-right').click()
					print('Despues del click')  
					
					pag += 1

				except NoSuchElementException:
					break

				except TimeoutException:
					trys2 = 1

					while trys2 <= 3:
						try:
							print('\n', '#'*15,'FALLO EL CLICK, ¡ COMENZAMOS !', '#'*15, '\n') 
							driver.refresh()
							break
							
						except:
							print('FALLO INTENTO DEL CLICK')
							trys2 += 1

					continue


		if n_cat < len(categories)-1:
			n_cat += 1

			yield Request(url= response.url,
						  callback= self.first_parse_cats,
						  meta= {'n_cat': n_cat,
								 'categories': categories},
						  dont_filter= True)            
		else:
			print('\n', '='*20,'\n', 'TAL PARECE QUE SE EXTRAJO TODA LA INFORMACION DE LA PAGINA !!','\n', '='*20, '\n')


