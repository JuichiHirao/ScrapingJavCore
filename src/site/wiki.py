import re
import urllib.request
from bs4 import BeautifulSoup
from .. import db
from .. import common
from .. import data


class Google:

    def __init__(self, max_result: int = 5):
        self.main_url = 'https://www.google.com/search?q=wiki+'
        self.opener = urllib.request.build_opener()
        self.opener.addheaders = [('User-Agent',
                                   'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]

        self.env = common.Environment()
        self.driver = self.env.get_driver()
        self.import_dao = db.import_dao.ImportDao()

        self.max_result = max_result

    def get_info(self, product_number):

        url = self.main_url + product_number

        urllib.request.install_opener(self.opener)

        site_name = ''
        site_url = ''
        with urllib.request.urlopen(url) as response:
            html = response.read()
            google_result_soup = BeautifulSoup(html, "html.parser")
            div_r_list = google_result_soup.findAll('div', class_='r')

            for idx, div_r in enumerate(div_r_list):
                a_div_r = div_r.find('a')
                url = a_div_r['href']

                print('Google ' + product_number + ' ' + url)

                if 'shecool.net' in url:
                    site_name = 'shecool.net'
                    site_url = url
                    break

                if 'sougouwiki.com' in url and '/d/' in url:
                    site_name = '総合wiki'
                    site_url = url
                    break

                if 'seasaawiki.jp' in url:
                    site_name = 'seasaaWiki'
                    site_url = url
                    break

                if 'avwikich.com' in url:
                    site_name = 'AVWikiCh'
                    site_url = url
                    break

                if idx > 8:
                    break

        return site_name, site_url

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


class SougouWiki:

    def __init__(self):

        self.search_url = 'http://sougouwiki.com/search?keywords='

        self.opener = urllib.request.build_opener()
        self.opener.addheaders = [('User-Agent',
                                        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]

        self.jav_dao = db.jav.JavDao()
        self.import_dao = db.import_dao.ImportDao()

    def __get_info(self, product_number):

        url = self.search_url + product_number

        result_search = ''
        urllib.request.install_opener(self.opener)
        with urllib.request.urlopen(url) as response:
            html = response.read()
            html_soup = BeautifulSoup(html, "html.parser")
            result_box = html_soup.find('div', class_='result-box')
            # print(len(result_box))

            # p_title = result_box.find('p', class_='title').text
            # print(p_title)

            wikis = result_box.findAll('h3', class_='keyword')
            len_wikis = len(wikis)

            if len_wikis > 0:
                wiki_list = []
                for idx, wiki in enumerate(wikis):
                    a = wiki.find('a')
                    # print(str(idx), str(a))
                    url = a['href']
                    wiki_list.append(a.text + ' ' + url)
                    # print(a.text + ' ' + url)

                result_search = '\n'.join(wiki_list)

        urllib.request.urlcleanup()

        return result_search

    def search(self, product_number):

        return self.__get_info(product_number)

    def test_execute(self):

        # javs = self.jav_dao.get_where_agreement('WHERE id = 1384')

        # result = self.search(javs[0].productNumber)
        # self.jav_dao.update_search_result(result, javs[0].id)

        imports = self.import_dao.get_all()
        if len(imports) > 0:
            for one_data in imports:
                result = self.search(one_data.productNumber)
                if len(result) > 0:
                    print(one_data.copy_text)
                    print(result)
                    print('')
                    self.import_dao.update_search_result(result, one_data.id)


if __name__ == '__main__':

    wiki = SougouWiki()
    wiki.test_execute()
