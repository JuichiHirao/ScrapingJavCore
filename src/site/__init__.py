import urllib.request
import requests
import re
from bs4 import BeautifulSoup
from . import fc2
from . import wiki
from . import mgs
from . import hey
from . import fanza
from .. import data
from .. import common


class SiteInfoCollect:

    def __init__(self):
        self.fanza = None
        self.fc2 = None
        self.hey = None
        self.mgs = None
        self.sougou_wiki = None
        self.google_wiki = None
        self.site_wiki = None
        self.copy_text = common.CopyText(False)

    def initialize(self):

        if self.sougou_wiki is None:
            self.sougou_wiki = wiki.SougouWiki()
            self.google_wiki = wiki.Google()
            self.site_wiki = wiki.Site()

        if self.fanza is None:
            self.fanza = fanza.Fanza()

        if self.fc2 is None:
            self.fc2 = fc2.Fc2()

        if self.hey is None:
            self.hey = hey.Hey()

        if self.mgs is None:
            self.mgs = mgs.Mgs()


class SiteInfoGetter:

    def __init__(self, site_collect: SiteInfoCollect = None, is_debug: bool = False, maker_parser: common.AutoMakerParser() = None):
        self.match_sell_date = '[12][0][0-9][0-9][-/][0-1][0-9][-/][0-3][0-9]'
        self.is_debug = is_debug

        if site_collect is None:
            self.site_collect = SiteInfoCollect()
            self.site_collect.initialize()
        else:
            self.site_collect = site_collect

        self.maker_parser = common.AutoMakerParser()
        # self.maker_parser = maker_parser

    def get_info(self, jav: data.JavData = None, match_maker: data.MakerData = None):

        site_data = None

        if match_maker.name == 'SITE':
            return site_data

        if site_data is None and 'HEY動画' in match_maker.name:
            site_data = self.site_collect.hey.get_info(jav.productNumber)

        if site_data is None and 'MGS' in match_maker.name or match_maker.siteKind == 2:
            site_data = self.site_collect.mgs.get_info(jav.productNumber)

        if site_data is None and 'FC2' in match_maker.name:
            site_data = self.site_collect.fc2.get_info(jav.productNumber)

        if site_data is None and match_maker.kind == 1:
            if match_maker.siteKind != 3 and match_maker.siteKind != 4:
                site_data = self.site_collect.fanza.get_info(jav.productNumber)

            if site_data is None:
                title = self.site_collect.copy_text.get_title(jav.title, jav.productNumber, match_maker)
                site_data = self.site_collect.fanza.get_info_from_title(title, jav.productNumber)

        if site_data is None and match_maker.kind == 3:
            stream_date = self.site_collect.copy_text.get_date_ura(jav.title)
            if len(stream_date) > 0:
                site_data = data.SiteData()
                site_data.streamDate = stream_date

        return site_data

    def get_wiki(self, jav: data.JavData = None, match_maker: data.MakerData = None):

        if match_maker.kind != 1:
            return ''

        if match_maker.name == 'SITE':
            site_name, site_url = self.site_collect.site_wiki.get_info(match_maker, jav.productNumber)
            result_search = site_name + ' ' + site_url
        else:
            if match_maker.siteKind == 3:
                result_search = self.site_collect.sougou_wiki.search(jav.productNumber)
            # elif match_maker.siteKind == 0:
            else:
                site_name, site_url = self.site_collect.google_wiki.get_info(jav.productNumber)
                result_search = site_name + ' ' + site_url

                if len(site_name) <= 0:
                    result_search = self.site_collect.sougou_wiki.search(jav.productNumber)

        return result_search

    def get_contents_info(self, jav: data.JavData = None, result_search: str = ''):

        if len(result_search.strip()) <= 0:
            return ''

        result_search_list = result_search.strip().split(' ')
        if len(result_search_list) <= 1:
            return ''

        if 'sougouwiki.com' in result_search.strip():
            response = requests.get(result_search_list[1])
            response.encoding = 'euc_jp'
            html = response.text
            html_soup = BeautifulSoup(html, 'html.parser')
        else:
            with urllib.request.urlopen(result_search_list[1]) as response:
                html = response.read()
                html_soup = BeautifulSoup(html, 'html.parser')

        if html_soup is None:
            return ''

        actress_name = ''
        site_data = None
        if 'shecool.net' in result_search.strip():
            site_data = self.__get_info_shecool(jav, html_soup)
            # site_data.print('    ')
        if 'avwikich.com' in result_search.strip():
            site_data = self.__get_info_avwikich(jav, html_soup)
            # site_data.print('    ')
        if 'sougouwiki.com' in result_search.strip():
            site_data = self.__get_info_sougouwiki(jav, html_soup)
            # site_data.print('    ')
        if 'seesaawiki.jp' in result_search.strip():
            site_data = self.__get_info_seesaawiki(jav, html_soup)
            # site_data.print('    ')

        if site_data is not None and len(site_data.actress.strip()) > 0:
            site_data.actress = self.maker_parser.apply_replace_info(site_data.actress, ('actress',))
            site_data.actress = site_data.actress.replace('？', '').replace('?', '')

        return site_data

    def __get_info_shecool(self, jav: data.JavData = None, html_soup: BeautifulSoup = None):

        site_data = data.SiteData()

        contents_list = html_soup.findAll('div', class_='s-contents')
        # print('contents_list ' + str(len(contents_list)))

        is_match = False
        for idx, div_c in enumerate(contents_list):
            a_name = div_c.find('a')
            if a_name is not None:
                site_data.actress = a_name.text
                # print('  a_text ' + str(a_name_text.text))

            span_c = div_c.findAll('span')
            for idx, span_text in enumerate(span_c):
                if re.search(self.match_sell_date, span_text.text):
                    m = re.search(self.match_sell_date, span_text.text)
                    # print('match sell_date ' + str(m.group()))
                    site_data.streamDate = m.group()
                # print('  span_text ' + span_text.text)
                if jav.productNumber in span_text.text:
                    is_match = True
                    # print(actress_name)

            if is_match:
                break
            else:
                site_data.streamDate = ''
                site_data.actress = ''

        return site_data

    def __get_info_avwikich(self, jav: data.JavData = None, html_soup: BeautifulSoup = None):

        site_data = data.SiteData()

        contents_list = html_soup.findAll('div', class_='entry-content')
        # print('contents_list ' + str(len(contents_list)))

        is_match = False
        for div_c in contents_list:
            a_name = div_c.find('a')
            if a_name is not None:
                site_data.actress = a_name.text
                # print('  a_text ' + str(a_name_text.text))

            span_c = div_c.findAll('span')
            for span_text in span_c:
                if '女優' in span_text.text:
                    site_data.actress = m.group()
                    site_data.actress = re.sub('出演女優名.*：', '', span_text.text)
                    # print('actress ' + actress_name)
                # print('  span_text ' + span_text.text)
                if re.search('[12][0][0-9][0-9][-/][0-1][0-9][-/][0-3][0-9]', span_text.text):
                    m = re.search(self.match_sell_date, span_text.text)
                    # print('avwiki match sell_date ' + str(m.group()))
                    site_data.streamDate = m.group()

                if jav.productNumber in div_c.text:
                    is_match = True

            if is_match:
                break

        return site_data

    def __get_info_sougouwiki(self, jav: data.JavData = None, html_soup: BeautifulSoup = None):

        site_data = data.SiteData()

        # main_table = html_soup.find('table', class_='edit')
        main_tables = html_soup.findAll('table')
        td_data_list = ['', '', '', '', ''] # 0 pNum, 1 img, 2 title, 3 a_name, 4 date
        is_match = False
        for table in main_tables:
            # td_data_list = [] # 0 pNum, 1 img, 2 title, 3 a_name, 4 date
            tr_list = table.findAll('tr')
            for tr in tr_list:
                td_list = tr.findAll('td', recursive=False)

                idx = 0
                for td in td_list:
                    print(str(idx) + ' ' + td.text)
                    td_data_list[idx] = td.text
                    # td_data_list.append(td.text)
                    if jav.productNumber in td.text:
                        # str_euc = tr.text
                        # print(tr.text)
                        # print(unicode(tr.text, "utf-8"))
                        is_match = True
                    idx = idx + 1

                    if idx >= 5:
                        break

                if is_match:
                    print(str(td_data_list))
                    site_data.actress = td_data_list[3]
                    site_data.streamDate = td_data_list[4]
                    break
                else:
                    site_data.actress = ''

            if is_match:
                break

        return site_data

    def __get_info_seesaawiki(self, jav: data.JavData = None, html_soup: BeautifulSoup = None):

        site_data = data.SiteData()

        main_tables = html_soup.findAll('table')
        td_data_list = ['', '', '', '', ''] # 0 pNum, 1 img, 2 title, 3 a_name, 4 date
        is_match = False
        for table in main_tables:
            # td_data_list = [] # 0 pNum, 1 name, 2 img, 3 a_name
            tr_list = table.findAll('tr')
            for tr in tr_list:
                td_list = tr.findAll('td', recursive=False)

                idx = 0
                for td in td_list:
                    a_href = td.find('a')
                    if a_href is not None:
                        href_text = a_href['href']
                    else:
                        href_text = ''

                    # print(str(idx) + ' ' + td.text + ' ' + href_text)
                    td_data_list[idx] = td.text

                    if len(href_text) > 0 and jav.productNumber in href_text:
                        # print(tr.text)
                        is_match = True
                    idx = idx + 1

                    if idx >= 5:
                        break

                if is_match:
                    print(str(td_data_list))
                    site_data.actress = td_data_list[3]
                    # site_data.streamDate = td_data_list[4]
                    break
                else:
                    site_data.actress = ''

            if is_match:
                break

        return site_data

