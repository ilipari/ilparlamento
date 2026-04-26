from typing import Any

import scrapy
from scrapy.http import Response
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class CameraSpider(CrawlSpider):
    name = "camera"
    allowed_domains = ["www.camera.it"]
    start_urls = ["https://www.camera.it/deputati/elenco"]

    rules = (
        Rule(
            LinkExtractor(allow=r"deputati\/elenco\?leg=19&lettera=[a-zA-Z]$"),
            callback="parse_list",
            follow=True
        ),
        Rule(
            LinkExtractor(allow=r"deputati/elenco/19-"),
            callback="parse_item"
        ),

    )

    def parse_start_url(self, response: Response, **kwargs: Any) -> Any:
        return ()

    def parse_item(self, response):
        item = {}
        #item["domain_id"] = response.xpath('//input[@id="sid"]/@value').get()
        #item["name"] = response.xpath('//div[@id="name"]').get()
        #item["description"] = response.xpath('//div[@id="description"]').get()
        return item

    def parse_list(self, response):
        item = {}
        #item["domain_id"] = response.xpath('//input[@id="sid"]/@value').get()
        #item["name"] = response.xpath('//div[@id="name"]').get()
        #item["description"] = response.xpath('//div[@id="description"]').get()
        return item