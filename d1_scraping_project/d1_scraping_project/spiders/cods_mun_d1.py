from scrapy import Spider
from scrapy.http import Request


from json import loads, dump




class CodsMunD1Spider(Spider):
	name = 'cods_mun_d1'
	allowed_domains = ['domicilios.tiendasd1.com']
	start_urls = ['http://domicilios.tiendasd1.com//']

	def parse(self, response):
		yield Request(url= 'https://domicilios.tiendasd1.com/api/citiesEst/127',
					  callback= self.first_parse,
					  headers= {'Accept': '*/*',
								'Accept-Encoding': 'gzip, deflate, br',
								'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
								'Authorization': 'datoschefmenu',
								'Connection': 'keep-alive',
								'Content-Type': 'application/json',
								'DNT': '1',
								'Host': 'domicilios.tiendasd1.com',
								'Referer': 'https://domicilios.tiendasd1.com/',
								'TE': 'Trailers',
								'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0'})

	def first_parse(self, response):
		print()
		print(response.url)
		print()
		print(response.status)
		print()

		jsonresponse = loads(response.body)
		jsonresponse = jsonresponse['listpais'][0]['listdep']

		ciudades_data = []
		i = 1
		for region in jsonresponse:
			for ciudad in region['listciu']:
				
				ciudad_info = {}

				print()
				print(i, '-', ciudad['nomciudad'])

				ciudad_info['cod_ciudad'] = ciudad['idciudad']
				ciudad_info['tipogeo'] = ciudad['tipogeo']

				ciudades_data.append(ciudad_info)
				i += 1
		print()

		n_mun = 0

		final_json = []

		yield Request(url= 'http://domicilios.tiendasd1.com//',
					  callback= self.second_parse,
					  meta= {'ciudades_data': ciudades_data,
					  		 'n_mun': n_mun,
					  		 'final_json': final_json},
					  dont_filter= True)



	def second_parse(self, response):
		ciudades_data = response.meta['ciudades_data']
		n_mun = response.meta['n_mun']
		final_json = response.meta['final_json']

		ciudad_data = ciudades_data[n_mun]


		yield Request(url= 'https://domicilios.tiendasd1.com/api/covertura/127/'+ str(ciudad_data['cod_ciudad']) +'/CL/1/1/1/'+ ciudad_data['tipogeo'] +'/-1/N/IA==/D1COL',
					  callback= self.third_parse,
					  meta= {'ciudades_data': ciudades_data,
					  		 'n_mun': n_mun,
					  		 'final_json': final_json},
					  headers= {'Accept': '*/*',
								'Accept-Encoding': 'gzip, deflate, br',
								'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
								'Authorization': 'datoschefmenu',
								'Connection': 'keep-alive',
								'Content-Type': 'application/json',
								'DNT': '1',
								'Host': 'domicilios.tiendasd1.com',
								'Referer': 'https://domicilios.tiendasd1.com/',
								'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0'},
					  dont_filter= True)


	def third_parse(self, response):
		print()
		print(response.url)
		print()
		print(response.status)
		print()

		ciudades_data = response.meta['ciudades_data']
		n_mun = response.meta['n_mun']
		final_json = response.meta['final_json']

		cod_soft = loads(response.body)['codSofwareExterno']

		print(cod_soft)

		yield Request(url= 'https://domicilios.tiendasd1.com/api/stockPrice/'+ cod_soft +'/D1COL',
					  callback= self.main_parse,
					  meta= {'ciudades_data': ciudades_data,
					  		 'n_mun': n_mun,
					  		 'final_json': final_json},
					  headers= {'Accept': '*/*',
								'Accept-Encoding': 'gzip, deflate, br',
								'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
								'Authorization': 'datoschefmenu',
								'Connection': 'keep-alive',
								'Content-Type': 'application/json',
								'DNT': '1',
								'Host': 'domicilios.tiendasd1.com',
								'Referer': 'https://domicilios.tiendasd1.com/',
								'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0'},
					  dont_filter= True)



	def main_parse(self, response):

		ciudades_data = response.meta['ciudades_data']
		n_mun = response.meta['n_mun']
		final_json = response.meta['final_json']
		

		print()
		print(response.url)
		print()
		print(response.status)
		print()

		prices_mun = loads(response.body)

		if final_json == []:
			final_json = prices_mun['prices']
		
		else:
			for prices in prices_mun['prices']:
				test = 0
				price = prices['art']

				for price_test in final_json:
					if price == price_test['art']:
						test += 1


				if test == 0:
					final_json.append(prices)

		if n_mun < len(ciudades_data) - 1:
			n_mun += 1

			yield Request(url= 'http://domicilios.tiendasd1.com//',
					  	  callback= self.second_parse,
					   	  meta= {'ciudades_data': ciudades_data,
						  		 'n_mun': n_mun,
						  		 'final_json': final_json},
						  dont_filter= True) 

		else:
			
			with open('final_json_prices_d1.json', 'w') as archivo:
				dump({'prices': final_json}, archivo)

			print('Terminamos !! ')
