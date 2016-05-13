from base64 import b64decode
import csv
from collections import defaultdict
import os.path
from functools import partial
from urllib.parse import urlsplit
import uuid

import scrapy
from scrapy.linkextractors import LinkExtractor
import scrapy_splash

from . import items


class Spider(scrapy.Spider):
    name = 'spider'

    def start_requests(self):
        self.start_urls = []
        self.requests_by_domain = defaultdict(int)
        self.domains_with_captcha = set()
        with open('OnionList.csv') as f:
            reader = csv.reader(f)
            for url, port, _ in reader:
                self.start_urls.append('http://{}.onion{}'.format(
                    url, '' if port == '80' else ':{}'.format(port)))
        for url in self.start_urls:
            yield self.request(url, domain=urlsplit(url).netloc)

    def request(self, url, domain):
        return scrapy_splash.SplashRequest(
            url,
            endpoint='render.json',
            args={'png': 1, 'html': 1},
            callback=partial(self.parse, domain=domain),
        )

    @staticmethod
    def has_captcha(response):
        body = '\n'.join(response.xpath('//body').extract())
        return 'captcha' in body.lower()

    def parse(self, response, domain=None):
        assert domain is not None
        if domain in self.domains_with_captcha:
            return
        item_id = uuid.uuid4()
        has_captcha = self.has_captcha(response)
        if has_captcha:
            self.domains_with_captcha.add(domain)
            with open(os.path.join(
                    'out', 'screenshots', '{}.png'.format(item_id)), 'wb') as f:
                f.write(b64decode(response.data['png']))
            with open(os.path.join(
                    'out', 'html', '{}.html'.format(item_id)), 'w') as f:
                f.write(response.text)
        yield items.Item(
            id=item_id,
            has_captcha=has_captcha,
            url=response.url,
        )
        if not has_captcha:
            link_extractor = LinkExtractor(allow_domains=domain)
            for link in link_extractor.extract_links(response):
                yield self.request(link.url, domain)
                self.requests_by_domain[domain] += 1
                if self.requests_by_domain[domain] > \
                        self.settings.getint('MAX_DOMAIN_REQUETS'):
                    break
