from typing import Any
from urllib.parse import urlparse, parse_qs

from dateparser import DateDataParser
from scrapy import Request, Spider
from scrapy.http import Response
from scrapy.linkextractors import LinkExtractor
import re

from scraper.request import ParlamentoCrawlRequest


def legislatura_from_url(url, legislatura_param='leg'):
    value = parametro_from_url(url, legislatura_param)
    if value:
        value = int(value)
    return value


def parametro_from_url(url, param):
    params = parse_qs(urlparse(url).query)
    value = params.get(param, [None])[0]
    return value


class CameraSpider(Spider):
    name = 'camera'
    allowed_domains = ['www.camera.it']
    start_urls = ['https://www.camera.it/deputati/elenco']
    list_by_letter_link_extractor = LinkExtractor(allow=r'deputati\/elenco\?leg=\d+&lettera=[a-zA-Z]$')
    date_parser = DateDataParser(languages=['it'])

    def __init__(self, *args, **kwargs):
        super(CameraSpider, self).__init__(*args, **kwargs)
        self.request = ParlamentoCrawlRequest({0}, ['B', 'M'], ['BITONCI', 'MELONI', 'MURA', 'MATONE'])
        self.date_fields =['DATA DI NASCITA',
                           'ELEZIONE CONVALIDATA',
                           'PROCLAMAZIONE',
                           'CESSAZIONE DAL MANDATO PARLAMENTARE']

    async def start(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse_start_url)

    def parse_start_url(self, response: Response, **kwargs: Any) -> Any:
        legislatura, _ = self.get_legislatura_e_lettera(response)
        self.request.normalize_legislature(legislatura)

        new_requests = self.parse_legislatura_landing_page(response) or []
        requested_leg = self.request.legislature.copy()
        legislatura_links_extractor = LinkExtractor(allow=r"deputati\/elenco\?leg=\d+$")
        for link in legislatura_links_extractor.extract_links(response):
            leg = legislatura_from_url(link.url, 'leg')
            if leg in requested_leg:
                requested_leg.remove(leg)
            if self.request.is_included(leg):
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
            if self.request.is_included(current_legislatura, current_lettera) \
            else []

        requested_lettere = self.request.lettere.copy()
        for link in CameraSpider.list_by_letter_link_extractor.extract_links(response):
            legislatura = legislatura_from_url(link.url, 'leg')
            lettera = parametro_from_url(link.url, 'lettera')
            if lettera in requested_lettere:
                requested_lettere.remove(lettera)
            if self.request.is_included(legislatura, lettera):
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
                self.logger.debug('link to legislatura %d and lettera %s - ignoring it cause was not requested', legislatura, lettera)
        if requested_lettere:
            self.logger.warning('not found link to requested lettere %s for legislature %d', requested_lettere, legislatura)
        return new_requests

    def parse_letter_index_page(self, response: Response, legislatura, lettera):
        new_requests = []
        if self.request.is_included(legislatura, lettera):
            self.logger.info('index for legislatura %d and lettra %s - searching deputy links', legislatura, lettera)
            link_extractor = LinkExtractor(allow=r"deputati\/elenco\/\d+-\d+$", restrict_css='.deputato-info', strip=True)
            for link in link_extractor.extract_links(response):
                cognome_nome = link.text.strip()
                if self.request.is_included(legislatura, lettera, cognome_nome):
                    self.logger.info('link to deputy %s in legislatura %d - following it', cognome_nome, legislatura)
                    follow = response.follow(
                        link,
                        callback=self.parse_deputato_page,
                        cb_kwargs={
                            'legislatura': legislatura,
                            'cognome_nome': cognome_nome
                        })
                    new_requests.append(follow)
                else:
                    self.logger.info('link to deputy %s in legislatura %d - ignoring it cause was not requested', cognome_nome, legislatura)
        else:
            self.logger.debug('index for legislatura %d and lettra %s - ignoring it cause was not requested', legislatura, lettera)
        return new_requests

    def parse_deputato_page(self, response: Response, legislatura, cognome_nome):
        nome_cognome = response.css('.deputato-nome::text').get().strip()
        self.logger.info('scraped deputy %s', nome_cognome)
        deputy = {
            'nome_cognome': nome_cognome,
            'cognome_nome': cognome_nome,
            'legislatura': legislatura
        }
        # anagrafica
        anagrafica_prop = response.css('.scheda-anagrafica-container ul.left-column li')
        for li in anagrafica_prop:
            pname = li.css('span::text').get()
            if pname.startswith('(IN SOSTITUZIONE DEL DEPUTATO') or pname.startswith('SOSTITUITO DA'):
                pvalue = li.css('a::text').get()
            else:
                pvalue = li.css('strong::text').get()
            # date fields
            if pname in self.date_fields:
                pvalue = self.parse_dates(pvalue)[0]
            deputy[pname] = pvalue

        # gruppi ed incarichi parlamentari
        deputy['gruppi'] = self.parse_simple_panel(response, 'GRUPPO PARLAMENTARE')
        self.add_roles(response, 'INCARICHI NEI GRUPPI PARLAMENTARI', deputy['gruppi'])
        deputy['organi'] = self.parse_simple_panel(response, 'COMPONENTE DEGLI ORGANI PARLAMENTARI')
        self.add_roles(response, 'UFFICI PARLAMENTARI', deputy['organi'])
        deputy['governo'] = self.parse_simple_panel(response, 'INCARICHI DI GOVERNO')
        return deputy

    def find_panel(self, response, title):
        panels = response.css('div.blue-div')
        for panel in panels:
            panel_title = panel.css('h3::text').get()
            if panel_title == title:
                return panel

    def parse_simple_panel(self, response, title):
        items = None
        panel = self.find_panel(response, title)
        if panel:
            items = []
            items_lis = panel.css('li')
            for item_li in items_lis:
                spans = item_li.css('span')
                item = {
                    'name': spans[0].css('::text').get()
                }
                dates = self.parse_dates(spans[1].css('::text').get())
                item['from_date'] = dates[0]
                item['to_date'] = dates[1] if len(dates) > 1 else None
                items.append(item)
        return items

    def add_roles(self, response, title, offices):
        panel = self.find_panel(response, title)
        if panel:
            items_lis = panel.css('li')
            for item_li in items_lis:
                spans = item_li.css('span')
                item = {
                    'name': spans[0].css('strong::text').get()
                }
                link_text = spans[0].css('a::text').get()
                if link_text:
                    office_name_container = link_text.strip()
                else:
                    office_name_container = spans[0].css('::text').getall()[-1].strip()

                dates = self.parse_dates(spans[1].css('::text').get())
                item['from_date'] = dates[0]
                item['to_date'] = dates[1] if len(dates) > 1 else None
                self.append_role_to_office(item, office_name_container, offices)

    def parse_roles_panel(self, response, title):
        items = None
        panel = self.find_panel(response, title)
        if panel:
            items = []
            items_lis = panel.css('li')
            for item_li in items_lis:
                spans = item_li.css('span')
                item = {
                    'role': spans[0].css('strong::text').get()
                }
                link_text = spans[0].css('a::text').get()
                if link_text:
                    item['office'] = link_text.strip()
                else:
                    item['office'] = spans[0].css('::text').getall()[-1].strip()

                dates = self.parse_dates(spans[1].css('::text').get())
                item['from_date'] = dates[0]
                item['to_date'] = dates[1] if len(dates) > 1 else None
                items.append(item)
        return items

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

    def parse_dates(self, riga, date_regex=r"\d{1,2} \w+ \d{4}", date_pattern='%d %B %Y'):
        # Converte le date in oggetti date
        dates = []
        match = re.findall(date_regex, riga)
        if match:
            for m in match:
                try:
                    date = CameraSpider.date_parser.get_date_data(m, [date_pattern]).date_obj.date()
                    dates.append(date)
                except Exception as e:
                    self.logger.exception('error parsing string %s', m)
                    raise e
        return dates

    def append_role_to_office(self, role, office_name_container, offices):
        for office in offices:
            if office['name'] in office_name_container:
                roles = office.get('roles', [])
                roles.append(role)
                office['roles'] = roles
                return
        raise NameError('impossibile assegnare il ruolo {} nell''ufficio {}'.format(role, office_name_container))
