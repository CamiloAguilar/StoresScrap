from scrapy import Spider
from scrapy.http import Request

import os, logging

from datetime import date


try:
	#os.mkdir(os.getcwd() + '\\logs')
	log_dir = os.getcwd() + '\\logs\\log_' + str(date.today()) + '.log'
	print(log_dir, '----------------------------- > log dir')
	logging.basicConfig(level= logging.DEBUG, format= '%(asctime)s : %(levelname)s : %(message)s', filename= log_dir, filemode = 'w')
	
except FileNotFoundError:
	os.mkdir(os.getcwd() + '\\logs')	
	log_dir = os.getcwd() + '\\logs\\log_' + str(date.today()) + '.log'
	
	logging.basicConfig(level= logging.DEBUG, format= '%(asctime)s : %(levelname)s : %(message)s', filename= log_dir, filemode = 'w')



def print_(message = ' ', type_ = 'info'):
	message = str(message)
	if type_ == 'deb': # deb es igual a debug
		logging.debug(message)
		#print(message)
	elif type_ == 'info': # info es igual a informacion
		logging.info(message)
		#print(message)
	elif type_ == 'war': # war es igual a warning
		logging.warning(message)
		#print(message)
	else:
		print('Mire que es corto lo que hay que escribir pa que se equivoque!!')



class KtronixScrapingSpider(Spider):
	name = 'ktronix_scraping'
	allowed_domains = ['ktronix.com']
	start_urls = ['http://ktronix.com/']
	#driver.quit()

	def parse(self, response):
			
		print_('#'*20+'INICIAMOS A TRABAJAR'+'#'*20, 'deb')		

		try: n_cat = response.meta['n_cat']
		except: n_cat = 2 

		#print('\n','#'*20, 'Este es n_cat !!', '\n', n_cat)
		print_()

		categories = response.xpath('//*[@class= "col-md-12 col-xs-12 scroll-mobile-grid"]//a/@href').extract()
		categories = ['https://www.ktronix.com' + category.strip() for category in categories]
		#print(categories)
		print_(categories)

		for i, n in enumerate(categories):
			print_(str(i)+'   '+str(n))

		category = categories[n_cat] 



		yield Request(url= category,
					  callback= self.category_parse,
					  meta= {'n_cat': n_cat,
							 'categories': categories,
							 'category': category},
					  dont_filter= True)


	def partial_parse(self, response):
		n_cat = response.meta['n_cat']
		categories = response.meta['categories']
		
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

		test = []

		try: n_subcat = response.meta['n_subcat']
		except: n_subcat = 0

		pag = 1

		print_()
		print_(response.url)
		print_()
		print_(response.status)
		print_()

		sub_categories = response.xpath('//*[@class= "col-4 col-xs-12"]/a/@href').extract()

		sub_category = sub_categories[n_subcat].replace('../..', '')

		print()
		print(sub_category)
		print()


		size = 25
		yield Request(url = 'https://www.ktronix.com' + sub_category,
					  callback= self.main_parse,
					  meta= {'n_cat': n_cat,
							 'categories': categories,
							 'category': category,
							 'test': test,
							 'n_subcat': n_subcat,
							 'pag': pag,
							 'sub_categories': sub_categories,
							 'sub_category': sub_category,
							 'size': size},
					  dont_filter= True)



	def main_parse(self, response):
		n_cat = response.meta['n_cat']
		categories = response.meta['categories']
		category = response.meta['category']
		test = response.meta['test']
		n_subcat = response.meta['n_subcat']
		pag = response.meta['pag']
		sub_categories = response.meta['sub_categories']
		sub_category = response.meta['sub_category']
		size = response.meta['size']

		test_2 = []

		prods = response.xpath('//*[@class= "product__listing product__list"]/li')
		cat_name = response.xpath('//*[@class= "col-xs-12 component__title"]/h1/text()').extract_first()
		if cat_name != []:
			cat_name = response.xpath('//*[@class= "col-xs-12 component__title"]/h1/text()').extract_first().strip()
		else: 
			cat_name = None

		for prod in prods:
			id_prod = prod.xpath('.//*[@class= "product__information"]/*[@class= "product__information--name"]/a/@data-id').extract_first()
			prod_name = prod.xpath('.//*[@class= "product__information"]/*[@class= "product__information--name"]/a/text()').extract_first()


			rating = prod.xpath('.//*[@class= "product__information"]//*[@class= "rating"]//@data-rating').extract_first()

			reviews = prod.xpath('.//*[@class= "product__information"]//*[@class= "review"]//text()').extract_first()
			if reviews != None: reviews = reviews.strip() 

			normal_price = prod.xpath('.//*[@class= "product__price"]//*[@class= "product__price--discounts__old "]/text()').extract()

			if normal_price != []:
				disc_price = prod.xpath('.//*[@class= "product__price"]//*[@class= "product__price--discounts__price"]/span[@class= "price"]/text()').extract_first().strip()
				normal_price = prod.xpath('.//*[@class= "product__price"]//*[@class= "product__price--discounts__old "]/text()').extract_first().strip()
			else:
				disc_price = prod.xpath('.//*[@class= "product__price"]//*[@class= "product__price--discounts__price"]/span[@class= "price"]/text()').extract_first().strip()
				normal_price = disc_price

			image_url = prod.xpath('.//*[@class= "product__image"]//*[@class= "product__image__container"]/img/@data-src').extract()

			if image_url != []:
				image_url = prod.xpath('.//*[@class= "product__image"]//*[@class= "product__image__container"]/img/@data-src').extract_first()
				image_url = 'https://www.ktronix.com' + image_url
			else:
				image_url = None

			print_('\n'+'#'*10+' Estamos en la pag '+ str(pag)+' '+'#'*10)
			print_(f'''
					   Categoria:  {cat_name}
					   Id: {id_prod}
					   Producto: {prod_name}

					   \tNormal price: {normal_price}
					   \tDisc price: {disc_price}
					   \tEstrellas: {rating}
					   \tReviews: {reviews}
				   ''')

			if pag == 1 and size == 25:
				test.append(id_prod)
			else:
				test_2.append(id_prod)


			if test != test_2:
				yield {
						'cat_name': cat_name,
						'id_prod': id_prod,
						'prod_name': prod_name,
						'disc_price': disc_price,
						'normal_price': normal_price,
						'rating': rating,
						'reviews': reviews,
						'image_url': image_url
				}

		if test != test_2:

			if pag == 1 and size == 25:
				size = 100
			else:
				pag += 1


			yield Request(url= 'https://www.ktronix.com' + sub_category + '?page='+str(pag)+'&pageSize='+str(size)+'&sort=relevance',
						  callback= self.main_parse,
						  meta= {'n_cat': n_cat,
								 'categories': categories,
								 'category': category,
								 'test': test,
								 'n_subcat': n_subcat,
								 'pag': pag,
								 'sub_categories': sub_categories,
								 'sub_category': sub_category,
								 'size': size},
						  dont_filter= True)

		elif test == test_2 and n_subcat < len(sub_categories)-1:
			n_subcat += 1
			yield Request(url= category,
						  callback= self.category_parse,
						  meta= {'n_cat': n_cat,
								 'categories': categories,
								 'category': category,
								 'n_subcat': n_subcat},
						  dont_filter= True)

		elif n_cat < len(categories) - 2:
			n_cat += 1
			yield Request(url= 'https://www.ktronix.com/',
						  callback= self.partial_parse,
						  meta= {'n_cat': n_cat,
								'categories': categories},
						  dont_filter= True)

		else:
			logging.shutdown()
			print_('#'*20+' Por ahora terminamos '+'#'*20)





# https://www.ktronix.com../../audio/audio-hogar/c/BI_112_KTRON?q=%3Arelevance%3Acategory%3ABI_0021_KTRON%3Acategory%3ABI_0023_KTRON%3Acategory%3ABI_0024_KTRON##
# https://www.ktronix.com/audio/audio-hogar/c/BI_112_KTRON?q=%3Arelevance%3Acategory%3ABI_0021_KTRON%3Acategory%3ABI_0023_KTRON%3Acategory%3ABI_0024_KTRON##