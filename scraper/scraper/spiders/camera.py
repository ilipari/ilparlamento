from typing import Any, List

from scrapy.http import Response
from scrapy.link import Link
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class CameraSpider(CrawlSpider):
    name = "camera"
    allowed_domains = ["www.camera.it"]
    start_urls = ["https://www.camera.it/deputati/elenco"]
    rules = (
        # estrae e segue i link agli elenchi dei deputati per lettera
        Rule(
            LinkExtractor(allow=r"deputati\/elenco\?leg=\d+&lettera=[a-zA-Z]$"),
            callback="parse_list",
            process_links="process_list_links",
            follow=True
        ),
        # estrae e segue i link alle altre legislature
        Rule(
            LinkExtractor(allow=r"deputati\/elenco\?leg=\d+$"),
            callback="parse_legislatura_landing_page",
            process_links="process_legislatura_links",
            follow=True
        ),
        # estrae i link delle pagine dei singoli deputati e fa il parsing delle pagine
        Rule(
            LinkExtractor(allow=r"deputati\/elenco\/\d+-\d+$"),
            callback="parse_deputato_page"
        ),
    )

    def __init__(self, legislature=None, lettere=None, *args, **kwargs):
        super(CameraSpider, self).__init__(*args, **kwargs)


    def parse_start_url(self, response: Response, **kwargs: Any) -> Any:
        return ()

    def process_list_links(self, links: List[Link], *args, **kwargs) -> Any:
        return links

    def parse_list(self, response):
        item = {}
        #item["domain_id"] = response.xpath('//input[@id="sid"]/@value').get()
        #item["name"] = response.xpath('//div[@id="name"]').get()
        #item["description"] = response.xpath('//div[@id="description"]').get()
        return item

    def process_legislatura_links(self, links: List[Link], *args, **kwargs) -> Any:
        return links

    def parse_legislatura_landing_page(self, response):
        # ricava la lettera corrente
        item = {}
        # item["domain_id"] = response.xpath('//input[@id="sid"]/@value').get()
        # item["name"] = response.xpath('//div[@id="name"]').get()
        # item["description"] = response.xpath('//div[@id="description"]').get()
        response.follow()
        return item

    def parse_deputato_page(self, response):
        referer = response.request.headers['Referer']
        item = {}
        #item["domain_id"] = response.xpath('//input[@id="sid"]/@value').get()
        #item["name"] = response.xpath('//div[@id="name"]').get()
        #item["description"] = response.xpath('//div[@id="description"]').get()
        return item
