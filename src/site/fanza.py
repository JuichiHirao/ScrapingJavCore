import re
import urllib.request
import urllib.error
import urllib.parse
from selenium.common import exceptions
from bs4 import BeautifulSoup
from .. import common
from .. import db
from .. import data


class Fanza:

    def __init__(self):
        self.main_url = 'https://www.google.com/search?q='
        self.url_suffix = '+fanza+av'
        self.opener = urllib.request.build_opener()
        self.opener.addheaders = [('User-Agent',
                                   'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]

        self.env = common.Environment()
        self.driver = self.env.get_driver()
        self.import_dao = db.import_dao.ImportDao()

    def get_info(self, p_number):

        site_data = None
        url = self.main_url + p_number + self.url_suffix

        split_p_number = p_number.split('-')
        urllib.request.install_opener(self.opener)

        try:
            with urllib.request.urlopen(url) as response:
                html = response.read()
                google_result_soup = BeautifulSoup(html, "html.parser")
                div_r_list = google_result_soup.findAll('div', class_='r')

                for idx, div_r in enumerate(div_r_list):
                    a_div_r = div_r.find('a')
                    url = a_div_r['href']

                    site_data = self.__get_and_check_site_data(p_number, split_p_number, url)

                    if site_data is not None:
                        break

                    if idx > 3:
                        break

        except AttributeError as aerr:
            print(str(aerr))
            print('error [' + url + ']')

        except urllib.error.URLError as uerr:
            print(str(uerr))
            print('error [' + url + ']')

        return site_data

    def get_info_from_title(self, title: str = '', p_number: str = ''):

        site_data = None

        if title is None:
            return site_data

        split_p_number = p_number.split('-')
        url = self.main_url + urllib.parse.quote_plus(title, encoding='utf-8') + self.url_suffix
        # print(url)

        urllib.request.install_opener(self.opener)

        try:
            with urllib.request.urlopen(url) as response:
                html = response.read()
                google_result_soup = BeautifulSoup(html, "html.parser")
                div_r_list = google_result_soup.findAll('div', class_='r')

                for idx, div_r in enumerate(div_r_list):
                    a_div_r = div_r.find('a')
                    url = a_div_r['href']

                    site_data = self.__get_and_check_site_data(p_number, split_p_number, url)

                    if site_data is not None:
                        break

                    if idx > 3:
                        break

        except AttributeError as aerr:
            print(str(aerr))
            print('error [' + url + ']')

        except urllib.error.URLError as uerr:
            print(str(uerr))
            print('error [' + url + ']')

        return site_data

    def __get_and_check_site_data(self, p_number: str = '', split_p_number: list = None, url: str = ''):
        site_data = None
        if len(split_p_number) >= 2:
            match_p_number = split_p_number[0] + '.*' + split_p_number[1]
        else:
            match_p_number = p_number

        if not re.search(match_p_number, url, re.IGNORECASE):
            return site_data

        # print('FANZA ' + product_number + ' ' + url)
        if 'www.dmm.co.jp' in url and '/detail/' in url:
            site_data = self.__parse_site_data(url)

        return site_data

    def __parse_site_data(self, url):

        self.driver.get(url)

        h1 = None
        try:
            h1 = self.driver.find_element_by_tag_name('h1')
        except exceptions.NoSuchElementException:
            print('h1 tag not found exceptions.NoSuchElementException')

        if h1 is None:
            print('h1 tag none')
            return None

        if '年齢認証' in h1.text:
            over18yes = self.driver.find_element_by_css_selector('.ageCheck__link--r18')
            # over18yes = self.driver.find_element_by_id('id')
            over18yes.click()

        html = self.driver.page_source
        html_soup = BeautifulSoup(html, "html.parser")

        table_info = html_soup.find('table', class_='mg-b20')
        # tr_all = table_info.findAll('tr')
        tr_all = table_info.findAll('tr')
        site_data = data.SiteData()
        h1_title = html_soup.find('h1', id='title')
        if h1_title:
            site_data.title = h1_title.text
        before_name = ''
        for idx, tr in enumerate(tr_all):
            for idx_sub, td in enumerate(tr.find_all_next('td')):
                # print(str(idx) + ' ' + str(idx_sub) + ' 【' + str(td.text) + '】')

                if before_name == '発売日':
                    site_data.streamDate = td.text.strip()
                    before_name = ''
                if re.search('発売日', td.text) or re.search('配信.*日', td.text):
                    before_name = '発売日'

                if before_name == 'duration':
                    site_data.duration = td.text.replace('\n', ' ').strip()
                    before_name = ''
                if re.search('収録時間', td.text):
                    before_name = 'duration'

                if before_name == 'actress':
                    site_data.actress = td.text.replace('\n', '').strip()
                    before_name = ''
                if re.search('出演者', td.text):
                    before_name = 'actress'

                if before_name == 'maker':
                    site_data.maker = td.text.strip()
                    before_name = ''
                if re.search('メーカー', td.text):
                    before_name = 'maker'

                if before_name == 'label':
                    site_data.label = td.text.strip()
                    before_name = ''
                if re.search('レーベル', td.text):
                    before_name = 'label'

                if before_name == 'series':
                    site_data.series = td.text.strip()
                    before_name = ''
                if re.search('シリーズ', td.text):
                    before_name = 'series'

            # print('tr end')
            # site_data.print()
            break

        # site_data.print()

        urllib.request.urlcleanup()

        return site_data
