import scrapy


class DiscoverhobbiesSpider(scrapy.Spider):
    name = 'discoverhobbies'
    base_url = 'https://www.discoverahobby.com/'
    start_urls = ['https://www.discoverahobby.com/']
    custom_settings = {
        "FEEDS": {
            "discover_hobbies.csv": {"format": "csv"},
            "discover_hobbies.json": {"format": "json"}
        }
    }

    def parse(self, response):
        for category in response.xpath('//div[@id="categories-wrap"]//div[@class="col-lg-3 col-md-6 category-item"]'):
            meta = {'category': category.xpath('.//h4/text()').get()}
            url = category.xpath('.//a/@href').get()
            yield scrapy.Request(url=url, meta=meta, callback=self.parse_category)

    def parse_category(self, response):
        for hobby_block in response.xpath('//div[@class="col-lg-3 col-md-6 col-sm-12"]'):
            yield {
                'name': hobby_block.xpath('.//h4/text()').get(),
                'image': self.base_url + hobby_block.xpath('.//img/@src').get(),
                'category': response.meta.get('category'),
                'hobby_detail_url': hobby_block.xpath('.//a/@href').get()
            }
