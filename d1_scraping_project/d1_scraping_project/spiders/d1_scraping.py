from scrapy import Spider
from scrapy.http import Request


from json import loads


def link_extend(url_str):
	if url_str[-1] != '/':
		return url_str + '/'
	else:
		return url_str


class D1ScrapingSpider(Spider):
	name = 'd1_scraping'
	allowed_domains = ['d1.com.co']
	start_urls = ['http://d1.com.co/']

	def parse(self, response):

		categories = response.xpath('//*[@id= "brand-discount-slider"]/ul/li/div[@class= "brand-logo-container"]/a/@href').extract()
		n_cat = 0


		l1 = []
		for n in categories:
			if n[-1] == '/':
				n = n[:-1]

			n = n[::-1].split('/', 2)[0][::-1].lower()

			l1.append(n)

		l1.append('extraordinario')

		categories = l1

		with open('./final_json_prices_d1.json') as json_file:

			price_list = loads(json_file.read())

		yield Request(url = 'https://d1.com.co/',
					  callback= self.second_parse,
					  meta= {'categories': categories,
							 'n_cat': n_cat,
							 'price_list': price_list})



	# def first_parse(self, response):
	# 	# print()
	# 	# print(response.url)
	# 	# print()
	# 	# print(response.status)
	# 	# print()
	# 	# print()
		




	def second_parse(self, response):
		price_list = response.meta['price_list']
		categories = response.meta['categories']
		n_cat = response.meta['n_cat']

		category = categories[n_cat]

		yield Request(url= 'https://domicilios.tiendasd1.com/page-data/'+category+'/page-data.json',
					  callback= self.main_parse,
					  meta= {'categories': categories,
							 'n_cat': n_cat,
							 'price_list': price_list,
							 'category': category},
					  dont_filter= True)



	def main_parse(self, response):
		price_list = response.meta['price_list']
		categories = response.meta['categories']
		n_cat = response.meta['n_cat']
		category = response.meta['category']

		print()
		print(response.url)
		print()
		print(response.status)
		print()

		jsonresponse = loads(response.body)

		cat_data = jsonresponse['result']['data']['ApisPrueba']['establishment']

		cat_data = cat_data['categories']['list']

		for cat in cat_data:
			sub_cat = cat['subCategory']

			cat_name = sub_cat['description']
			prods = sub_cat['articles']['list']

			for prod in  prods:

				prod_id = prod['id']
				prod_name = prod['name']

				normal_price = ''
				disc_price = ''
				unidades = ''

				for price in price_list['prices']:
					if prod_id == price['art']:
						normal_price = price['price']
						disc_price = price['price']
						unidades = price['stock']
						break

				image_url = prod['image']

				print('\nCategoria:\t', cat_name,
						  '\n\tProducto:\t', prod_name,
						  '\n\tNormal price:\t', normal_price,
						  '\n\tDiscount price:\t', disc_price,'\n')


				yield {'cat_name': cat_name,
					   'prod_name': prod_name,
					   'normal_price': normal_price,
					   'disc_price': disc_price,
					   'unidades': unidades,
					   'image_url': image_url}

		if n_cat < len(categories)-1:
			n_cat += 1

			yield Request(url = 'https://d1.com.co/',
					  	  callback= self.second_parse,
					  	  meta= {'categories': categories,
							 'n_cat': n_cat,
							 'price_list': price_list},
						  dont_filter= True)
		else: 
			print('\n', '='*20,'\n', 'TAL PARECE QUE SE EXTRAJO TODA LA INFORMACION DE LA PAGINA !!','\n', '='*20, '\n')

		

