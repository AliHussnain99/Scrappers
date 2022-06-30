import html

import scrapy
import json

from bs4 import BeautifulSoup

uncommon_api_endpoints = [
    'https://www.uncommongoods.com/br/search/?account_id=5343&domain_key=uncommongoods&request_type=search&br_origin=searchBox&search_type=keyword&fl=pid%2Ctitle%2Cthumb_image%2Cthumb_image_alt%2Curl%2Cprice_range%2Cis_customizable&q=*&rows={rows}&start={start}&url=%22%2Fthis-just-in&ref_url=%22%2Fthis-just-in%22',
    'https://www.uncommongoods.com/br/search/?account_id=5343&domain_key=uncommongoods&request_type=search&br_origin=searchBox&search_type=category&fl=pid%2Ctitle%2Cthumb_image%2Cthumb_image_alt%2Curl%2Cprice_range%2Cis_customizable&q=gifts&rows={rows}&start={start}&url=%22%2Fgifts&ref_url=%22%2Fgifts%22',
    'https://www.uncommongoods.com/br/search/?account_id=5343&domain_key=uncommongoods&request_type=search&br_origin=searchBox&search_type=category&fl=pid%2Ctitle%2Cthumb_image%2Cthumb_image_alt%2Curl%2Cprice_range%2Cis_customizable&q=homegarden&rows={rows}&start={start}&url=%22%2Fhome-garden&ref_url=%22%2Fhome-garden%22',
    'https://www.uncommongoods.com/br/search/?account_id=5343&domain_key=uncommongoods&request_type=search&br_origin=searchBox&search_type=category&fl=pid%2Ctitle%2Cthumb_image%2Cthumb_image_alt%2Curl%2Cprice_range%2Cis_customizable&q=kitchenbar&rows={rows}&start={start}&url=%22%2Fkitchen-bar&ref_url=%22%2Fkitchen-bar%22',
    'https://www.uncommongoods.com/br/search/?account_id=5343&domain_key=uncommongoods&request_type=search&br_origin=searchBox&search_type=category&fl=pid%2Ctitle%2Cthumb_image%2Cthumb_image_alt%2Curl%2Cprice_range%2Cis_customizable&q=jewelry&rows={rows}&start={start}&url=%22%2Fjewelry&ref_url=%22%2Fjewelry%22',
    'https://www.uncommongoods.com/br/search/?account_id=5343&domain_key=uncommongoods&request_type=search&br_origin=searchBox&search_type=category&fl=pid%2Ctitle%2Cthumb_image%2Cthumb_image_alt%2Curl%2Cprice_range%2Cis_customizable&q=forher&rows={rows}&start={start}&url=%22%2Ffor-her&ref_url=%22%2Ffor-her%22',
    'https://www.uncommongoods.com/br/search/?account_id=5343&domain_key=uncommongoods&request_type=search&br_origin=searchBox&search_type=category&fl=pid%2Ctitle%2Cthumb_image%2Cthumb_image_alt%2Curl%2Cprice_range%2Cis_customizable&q=forhim&rows={rows}&start={start}&url=%22%2Ffor-him&ref_url=%22%2Ffor-him%22'
    'https://www.uncommongoods.com/br/search/?account_id=5343&domain_key=uncommongoods&request_type=search&br_origin=searchBox&search_type=category&fl=pid%2Ctitle%2Cthumb_image%2Cthumb_image_alt%2Curl%2Cprice_range%2Cis_customizable&q=forkids&rows={rows}&start={start}&url=%22%2Ffor-kids&ref_url=%22%2Ffor-kids%22',
    'https://www.uncommongoods.com/br/search/?account_id=5343&domain_key=uncommongoods&request_type=search&br_origin=searchBox&search_type=category&fl=pid%2Ctitle%2Cthumb_image%2Cthumb_image_alt%2Curl%2Cprice_range%2Cis_customizable&q=fun&rows={rows}&start={start}&url=%22%2Ffun&ref_url=%22%2Ffun%22',
    'https://www.uncommongoods.com/br/search/?account_id=5343&domain_key=uncommongoods&request_type=search&br_origin=searchBox&search_type=category&fl=pid%2Ctitle%2Cthumb_image%2Cthumb_image_alt%2Curl%2Cprice_range%2Cis_customizable&q=featured&rows={rows}&start={start}&url=%22%2Ffeatured&ref_url=%22%2Ffeatured%22',
    'https://www.uncommongoods.com/br/search/?account_id=5343&domain_key=uncommongoods&request_type=search&br_origin=searchBox&search_type=category&fl=pid%2Ctitle%2Cthumb_image%2Cthumb_image_alt%2Curl%2Cprice_range%2Cis_customizable&q=*&rows={rows}&start={start}&url=%22%2Fsale&ref_url=%22%2Fsale%22'
]


def clean_text(text):
    soup = BeautifulSoup(text)
    return html.unescape(soup.get_text())


class UncommonSpider(scrapy.Spider):
    name = 'uncommon'
    base_url = 'https://www.uncommongoods.com'
    detail_url = 'https://www.uncommongoods.com/assets/get/item/v2/{product_url}?chunks=item'

    # custom_settings = {
    #     "FEEDS": {
    #         "uncommon_products.csv": {"format": "csv"},
    #         "uncommon_products.json": {"format": "json"}
    #     }
    # }

    def __init__(self):
        self.start = 0
        self.rows = 200
        self.uncommon_api_endpoints = uncommon_api_endpoints

    def start_requests(self):
        for url in self.uncommon_api_endpoints:
            cb_kwargs = {'url': url}
            url = url.format(rows=self.rows, start=self.start)
            yield scrapy.Request(url=url, cb_kwargs=cb_kwargs)

    def parse(self, response, url):
        data = json.loads(response.text)
        total_records = data['response']['numFound']
        total_requests = int(total_records / 200) + 1

        start = self.start

        paginated_requests = []
        for request in range(0, total_requests):
            formatted_url = url.format(rows=self.rows, start=start)
            start = start + self.rows
            paginated_requests.append(
                scrapy.Request(url=formatted_url, callback=self.parse_product)
            )
        yield from paginated_requests

    def parse_product(self, response):
        data = json.loads(response.text)['response']
        total_products = data['docs']

        product_detail_requests = []
        for product in total_products:
            meta = {
                'price_range': product.get('price_range'),
                'price': self.get_price(product.get('price_range')),
                'thumb_image': self.base_url + product.get('thumb_image', ''),
                'thumb_image_alt': self.base_url + product.get('thumb_image_alt', ''),
                'product_url': self.base_url + product.get('url', '')
            }
            detail_url = self.detail_url.format(product_url=product.get('url').split('/')[-1])
            product_detail_requests.append(
                scrapy.Request(url=detail_url, meta=meta, callback=self.parse_product_detail)
            )
        yield from product_detail_requests

    def parse_product_detail(self, response):
        product = json.loads(response.text)['item']
        yield {
            'product_id': product.get('item_id'),
            'title': clean_text(product.get('name')),
            'description': clean_text(product.get('long_desc')),
            'price': response.meta.get('price'),
            'price_range': response.meta.get('price_range'),
            'thumb_image': response.meta.get('thumb_image', ''),
            'thumb_image_alt': response.meta.get('thumb_image_alt', ''),
            'is_customizable': product.get('is_customizable'),
            'product_url': response.meta.get('product_url')
        }

    def get_price(self, price_range):
        return price_range[0] if price_range and price_range[0] == price_range[1] else None
