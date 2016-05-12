from base64 import b64decode
import csv
import os.path
from urllib.parse import urlsplit

import scrapy
import scrapy_splash

from . import items


class Spider(scrapy.Spider):
    name = 'spider'

    def start_requests(self):
        self.start_urls = []
        with open('OnionList.csv') as f:
            reader = csv.reader(f)
            for url, port, _ in reader:
                self.start_urls.append('http://{}.onion{}'.format(
                    url, '' if port == '80' else ':{}'.format(port)))
        for url in self.start_urls:
            yield scrapy_splash.SplashRequest(
                url,
                endpoint='render.json',
                args={'png': 1, 'html': 1},
            )

    def parse(self, response):
        has_captcha = 'captcha' in response.text.lower()
        domain = urlsplit(response.url).netloc
        filename = '{}.png'.format(domain)
        screenshot = b64decode(response.data['png'])
        paths = [os.path.join('out', 'all-screenshots', filename)]
        if has_captcha:
            paths.append(os.path.join('out', 'captcha-screenshots', filename))
        for path in paths:
            with open(path, 'wb') as f:
                f.write(screenshot)
        with open(os.path.join(
                'out', 'html-all', '{}.html'.format(domain)), 'w') as f:
            f.write(response.text)
        yield items.Item(
            url=response.url,
            has_captcha=has_captcha)
