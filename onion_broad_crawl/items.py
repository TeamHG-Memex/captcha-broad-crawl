import scrapy


class Item(scrapy.Item):
    url = scrapy.Field()
    has_captcha = scrapy.Field()
