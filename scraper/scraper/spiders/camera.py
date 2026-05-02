from typing import Any
from urllib.parse import urlparse, parse_qs

import scrapy
from scrapy import Request
from scrapy.http import Response
from scrapy.linkextractors import LinkExtractor


def normalize_requested_legislature(legislature, ultima_legislatura):
    normalized = []
    if legislature:
        normalized = map(lambda l: l if l > 0 else ultima_legislatura+l, legislature)
    return set(normalized)


def legislatura_from_url(url, legislatura_param='leg'):
    value = parametro_from_url(url, legislatura_param)
    if value:
        value = int(value)
    return value


def parametro_from_url(url, param):
    params = parse_qs(urlparse(url).query)
    value = params.get(param, [None])[0]
    return value


class CameraSpider(scrapy.Spider):
    name = 'camera'
    allowed_domains = ['www.camera.it']
    start_urls = ['https://www.camera.it/deputati/elenco']
    list_by_letter_link_extractor = LinkExtractor(allow=r'deputati\/elenco\?leg=\d+&lettera=[a-zA-Z]$')

    def __init__(self, *args, **kwargs):
        super(CameraSpider, self).__init__(*args, **kwargs)
        self.legislature = [-1, 19, 20]
        self.lettere = ['K']

    async def start(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse_start_url)

    def parse_start_url(self, response: Response, **kwargs: Any) -> Any:
        legislatura, _ = self.get_legislatura_e_lettera(response)
        self.legislature = normalize_requested_legislature(self.legislature, legislatura)

        new_requests = self.parse_legislatura_landing_page(response) or []
        requested_leg = self.legislature.copy()
        legislatura_links_extractor = LinkExtractor(allow=r"deputati\/elenco\?leg=\d+$")
        for link in legislatura_links_extractor.extract_links(response):
            leg = legislatura_from_url(link.url, 'leg')
            if leg in requested_leg:
                requested_leg.remove(leg)
                if leg != legislatura:
                    self.logger.info('link to legislatura %d, following it', leg)
                    new_requests.append(response.follow(link, callback=self.parse_legislatura_landing_page))
                else:
                    self.logger.debug('link to legislatura %d, ignoring it cause is landing one', leg)
            else:
                self.logger.debug('link to legislatura %d, ignoring it cause was not requested', leg)

        if requested_leg:
            self.logger.warning('not found link to requested legislature %s', requested_leg)
        return new_requests

    def parse_legislatura_landing_page(self, response: Response):
        # ricava la lettera corrente
        # cioè la lettera di default per la legislatura
        # esplora link alle altre lettere per la legislatura corrente
        current_legislatura, current_lettera = self.get_legislatura_e_lettera(response)
        new_requests = self.parse_letter_index_page(response, current_legislatura, current_lettera) \
            if self.is_requested(current_legislatura, current_lettera) \
            else []

        requested_lettere = self.lettere.copy()
        for link in CameraSpider.list_by_letter_link_extractor.extract_links(response):
            legislatura = legislatura_from_url(link.url, 'leg')
            lettera = parametro_from_url(link.url, 'lettera')
            if self.is_requested(legislatura, lettera):
                requested_lettere.remove(lettera)
                if lettera != current_lettera:
                    self.logger.info('link to legislatura %d and lettera %s - following it', legislatura, lettera)
                    follow = response.follow(
                        link,
                        callback=self.parse_letter_index_page,
                        cb_kwargs={
                            'legislatura': legislatura,
                            'lettera': lettera
                        })
                    new_requests.append(follow)
                else:
                    self.logger.debug('link to legislatura %d and lettera %s - ignoring it cause is landing lettera', legislatura. lettera)
            else:
                self.logger.debug('link to legislatura %d and lettra %s - ignoring it cause was not requested', legislatura, lettera)
        if requested_lettere:
            self.logger.warning('not found link to requested lettere %s for legislature %d', requested_lettere, legislatura)
        return new_requests

    def parse_letter_index_page(self, response: Response, legislatura, lettera):
        new_requests = []
        if self.is_requested(legislatura, lettera):
            self.logger.info('index for legislatura %d and lettra %s - searching deputy links', legislatura, lettera)
            link_extractor = LinkExtractor(allow=r"deputati\/elenco\/\d+-\d+$")
            for link in link_extractor.extract_links(response):
                follow = response.follow(
                    link,
                    callback=self.parse_deputato_page,
                    cb_kwargs={
                        'legislatura': legislatura
                    })
                new_requests.append(follow)
        else:
            self.logger.debug('index for legislatura %d and lettra %s - ignoring it cause was not requested', legislatura, lettera)
        return new_requests

    def parse_deputato_page(self, response: Response, legislatura):
        nome_cognome = response.css('.deputato-nome::text').get().strip()
        self.logger.info('scraped deputy %s', nome_cognome)
        deputy = {
            'nome': nome_cognome,
            'legislatura': legislatura
        }
        return deputy


    def get_legislatura_e_lettera(self, response: Response) -> Any:
        # ricava dalla pagina
        # - la legislatura corrente
        # - la lettera corrente (iniziale del cognome)
        legislatura = 0
        for link in CameraSpider.list_by_letter_link_extractor.extract_links(response):
            legislatura = legislatura_from_url(link.url, 'leg')
            if legislatura:
                break
        iniziale = response.css('.a-selected::text').get().strip()
        return legislatura, iniziale

    def is_requested(self, legislatura, lettera) -> bool:
        requested = True
        if legislatura and self.legislature:
            requested = requested and legislatura in self.legislature
        if lettera and self.lettere:
            requested = requested and lettera in self.lettere
        return requested
