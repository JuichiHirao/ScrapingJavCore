import re
import urllib.request
from bs4 import BeautifulSoup
from .. import common
from .. import db
from .. import data


class Fanza:

    def __init__(self):
        self.main_url = 'https://www.google.com/search?q=fanza+av+'
        self.opener = urllib.request.build_opener()
        self.opener.addheaders = [('User-Agent',
                                   'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]

        self.env = common.Environment()
        self.driver = self.env.get_driver()
        self.import_dao = db.import_dao.ImportDao()

    def get_info(self, product_number):

        site_data = None
        url = self.main_url + product_number

        urllib.request.install_opener(self.opener)

        with urllib.request.urlopen(url) as response:
            html = response.read()
            google_result_soup = BeautifulSoup(html, "html.parser")
            div_r_list = google_result_soup.findAll('div', class_='r')

            for idx, div_r in enumerate(div_r_list):
                a_div_r = div_r.find('a')
                url = a_div_r['href']

                print('FANZA ' + product_number + ' ' + url)
                if 'www.dmm.co.jp' in url and '/detail/' in url:
                    site_data = self.__parse_site_data(url)
                    break

                if idx > 3:
                    break

        return site_data

    def __parse_site_data(self, url):

        site_data = None
        with urllib.request.urlopen(url) as response:
            html = response.read()
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
