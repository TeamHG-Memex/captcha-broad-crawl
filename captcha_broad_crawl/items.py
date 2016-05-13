import scrapy


class Item(scrapy.Item):
    id = scrapy.Field()
    has_captcha = scrapy.Field()
    url = scrapy.Field()
