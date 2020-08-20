from scrapy import Spider
from scrapy.http import Request

from json import loads

try: driver.quit()
except: pass



def num_cat_func(num):
	if num < 10:
		return '0'+str(num)
	else:
		return str(num)




class ColsubsidioScrapingDrogSpider(Spider):
	name = 'colsubsidio_scraping_drog'
	allowed_domains = ['drogueriascolsubsidio.com']
	start_urls = ['http://drogueriascolsubsidio.com/']


	def parse(self, response):
		print()
		print(response.url)
		print()

		yield Request(url= response.url,
					  callback= self.drogueria_parse)



	def drogueria_parse(self, response):
		print()
		print(response.url, '------------------------> drogueria')
		print()

		n_cat = 0 
		n_min_subcat = 0
		gen_categories = response.xpath('//*[@class= "MenuContainer"]/ul/a/@href').extract()

		yield Request(url= response.url, 
					  callback= self.parse_secd,
					  meta= {'n_cat': n_cat,
							 'gen_categories': gen_categories,
							 'n_min_subcat': n_min_subcat},
					  dont_filter= True)




	def parse_secd(self, response):

		n_cat = response.meta['n_cat']
		gen_categories = response.meta['gen_categories']
		n_min_subcat = response.meta['n_min_subcat']

		gen_category = gen_categories[n_cat]
		
		yield Request(url= 'https://www.drogueriascolsubsidio.com' + gen_category,
					  callback= self.submain_drogueria,
					  meta= {'n_cat': n_cat,
							 'gen_categories': gen_categories,
							 'n_min_subcat': n_min_subcat,
							 'gen_category': gen_category})


	def submain_drogueria(self, response):

		n_cat = response.meta['n_cat']
		gen_categories = response.meta['gen_categories']
		n_min_subcat = response.meta['n_min_subcat']
		gen_category = response.meta['gen_category']

		sub_categs = response.xpath('//*[@class= "Container-FiltrosDepartamento"]//a/@href').extract()
		lengs = len(sub_categs)

		if 'belleza' in response.url:
			lengs += 1 ############################################### Tener en cuenta
		elif 'alimentos-y-bebidas' in response.url:
			lengs += 2 ############################################### Tener en cuenta


		sub_categs_len = lengs + n_min_subcat

		n_from = 0

		n_to = 40

		try: n_subcat = response.meta['n_subcat']
		except: n_subcat = n_min_subcat + 1
		
		cat_code = n_cat + 1
		n_subcat = num_cat_func(n_subcat)

		yield Request(url= 'https://www.drogueriascolsubsidio.com/api/catalog_system/pub/products/search?fq=C:'+str(cat_code)+'/'+str(cat_code)+n_subcat+'&_from='+str(n_from)+'&_to='+str(n_to)+'&sm=0&O=OrderByReleaseDateDESC',
					  callback= self.main_drogueria,
					  meta= {'n_cat': n_cat,
							 'gen_categories': gen_categories,
							 'n_from': n_from,
							 'n_to': n_to,
							 'sub_categs_len': sub_categs_len,
							 'cat_code': cat_code,
							 'n_subcat': n_subcat,
							 'n_min_subcat': n_min_subcat,
							 'gen_category': gen_category,
							 'lengs': lengs})

			

	def intermedio_parse(self, response):

		n_cat = response.meta['n_cat']
		gen_categories = response.meta['gen_categories']
		sub_categs_len = response.meta['sub_categs_len']
		n_from = response.meta['n_from']
		n_to = response.meta['n_to']
		cat_code = response.meta['cat_code']
		n_subcat = response.meta['n_subcat']	
		n_min_subcat = response.meta['n_min_subcat']
		gen_category = response.meta['gen_category']
		lengs = response.meta['lengs']

		yield Request(url= 'https://www.drogueriascolsubsidio.com/api/catalog_system/pub/products/search?fq=C:'+str(cat_code)+'/'+str(cat_code)+n_subcat+'&_from='+str(n_from)+'&_to='+str(n_to)+'&sm=0&O=OrderByReleaseDateDESC',
						  callback= self.main_drogueria,
						  meta= {'n_cat': n_cat,
								 'gen_categories': gen_categories,
								 'n_from': n_from,
								 'n_to': n_to,
								 'sub_categs_len': sub_categs_len,
								 'cat_code': cat_code,
								 'n_subcat': n_subcat,
								 'n_min_subcat': n_min_subcat,
								 'gen_category': gen_category,
								 'lengs': lengs},
						  dont_filter= True)








	def main_drogueria(self, response):
		
		n_cat = response.meta['n_cat']
		gen_categories = response.meta['gen_categories']
		sub_categs_len = response.meta['sub_categs_len']
		n_from = response.meta['n_from']
		n_to = response.meta['n_to']
		cat_code = response.meta['cat_code']
		n_subcat = response.meta['n_subcat']
		n_min_subcat = response.meta['n_min_subcat']
		gen_category = response.meta['gen_category']
		lengs = response.meta['lengs']

		jsonresponse = loads(response.body)
		#print(response.body)
		# sleep(3)
		# jsonresponse = loads(response.body)

		print(len(jsonresponse), '---------------> len')
		print()
		print(response.url)
		#print(jsonresponse)
	
		if response.body != b'[]':
			for prod in jsonresponse:

				cat_name = prod['categories'][-1]
				prod_name = prod['productTitle'].replace('"','')
				prod_name = prod['productTitle'].replace('\n','')

				normal_price = prod['items'][0]['sellers'][0]['commertialOffer']['PriceWithoutDiscount']
				disc_price = prod['items'][0]['sellers'][0]['commertialOffer']['Price']
				image_url = prod['items'][0]['images'][0]['imageUrl']

				unidades = prod['Unidades'][0]
				
				print(n_from, n_to, '-----------------------> n from n to')
				print('\nCategoria:\t', cat_name,
					  '\n\tProducto:\t', prod_name,
					  '\n\tNormal price:\t', normal_price,
					  '\n\tDiscount price:\t', disc_price,
					  '\n\tUnidades:\t', unidades, '\n')


				yield {'cat_name': cat_name,
					   'prod_name': prod_name,
					   'normal_price': normal_price,
					   'disc_price': disc_price,
					   'image_url': image_url,
					   'unidades': unidades,
					   'cat': n_subcat}

				#break

			n_from += 40
			n_to += 40
			yield Request(url= 'https://www.drogueriascolsubsidio.com/',
						  callback= self.intermedio_parse,
						  meta= {'n_cat': n_cat,
								 'gen_categories': gen_categories,
								 'n_from': n_from,
								 'n_to': n_to,
								 'sub_categs_len': sub_categs_len,
								 'cat_code': cat_code,
								 'n_subcat': n_subcat,
								 'n_min_subcat': n_min_subcat,
								 'gen_category': gen_category,
								 'lengs': lengs},
						  dont_filter= True)

		elif int(n_subcat) <= sub_categs_len:
			n_subcat = int(n_subcat) + 1

			yield Request(url= 'https://www.drogueriascolsubsidio.com' + gen_category,
						  callback= self.submain_drogueria,
						  meta= {'n_cat': n_cat,
								 'gen_categories': gen_categories,
								 'n_subcat': n_subcat,
								 'n_min_subcat': n_min_subcat,
								 'gen_category': gen_category},
						  dont_filter= True)


		elif n_cat < len(gen_categories) - 1:
			n_min_subcat += lengs
			n_cat += 1

			yield Request(url= 'https://www.drogueriascolsubsidio.com/',
						  callback= self.parse_secd,
						  meta= {'n_cat': n_cat,
								 'gen_categories': gen_categories,
								 'n_min_subcat': n_min_subcat},
						  dont_filter= True)

		else:
			'SE ACABO POR AHORA ESTA CATEGORIA'
