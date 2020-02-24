import urllib.request
import sys
import re
from time import sleep
from bs4 import BeautifulSoup
from .. import common
from .. import data


class Fc2:

    def __init__(self):
        self.main_url = 'http://adult.contents.fc2.com/article_search.php?id='
        self.opener = urllib.request.build_opener()
        self.opener.addheaders = [('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]

        self.env = common.Environment()

    def __get_info_from_chrome(self, product_number):

        self.driver = self.env.get_driver()

        # print(self.main_url + product_number)
        self.driver.get(self.main_url + product_number)

        sleep(1)

        site_data = None
        header_info = self.driver.find_elements_by_css_selector('.items_article_headerInfo')

        # block_text = header_info.text
        self.__get_site_data(header_info)
        # print(main_info.text)
        # site_data = self.__get_site_data(block_text.splitlines())

        self.driver.close()

        return site_data

    def __get_site_data(self, header_info):

        site_data = data.SiteData()
        li_list = header_info.find_all('li')
        release_date = header_info.find('div', class_='items_article_Releasedate')
        if release_date is not None:
            release_date_str = release_date.find('p').text
        else:
            release_date_str = ''

        for li in li_list:
            if 'by ' in li.text:
                site_data.maker = li.text.replace('by', '').replace('　', ' ').strip()
                print('label {}'.format(site_data.maker))

        site_data.streamDate = release_date_str.replace('販売日 : ', '')
        print('streamDate [{}]'.format(site_data.streamDate))

        return site_data

    def __get_site_data_backup(self, lines):

        site_data = data.SiteData()

        before_name = ''
        for line in lines:
            if before_name == 'sell_date':
                site_data.streamDate = line.strip()
                before_name = ''
            if re.search('販売日', line) or re.search('配信.*日', line):
                before_name = 'sell_date'

            if before_name == 'maker':
                site_data.maker = line.strip()
                before_name = ''
            if re.search('販売者', line):
                before_name = 'maker'

            if before_name == 'duration':
                site_data.duration = line.strip()
                before_name = ''
            if re.search('再生時間', line):
                before_name = 'duration'

        return site_data

    def __get_info(self, product_number):

        url = self.main_url + product_number
        urllib.request.install_opener(self.opener)

        with urllib.request.urlopen(url) as response:
            html = response.read()
            html_soup = BeautifulSoup(html, "html.parser")
            header_info = html_soup.find('div', class_='items_article_headerInfo')

            # block_text = header_info.text
            site_data = self.__get_site_data(header_info)

            # site_data = self.__get_site_data(block_text.splitlines())

        urllib.request.urlcleanup()

        return site_data

    def get_info(self, product_number):

        try:
            return self.__get_info(product_number)
            # return self.__get_info_from_chrome(product_number)
        except:
            print(sys.exc_info())
            return None


if __name__ == '__main__':

    # 正常
    fc2 = Fc2()
    seller, sell_date = fc2.get_info('872051')
    print(seller + ' [' + str(sell_date) + ']')

    # 該当無し
    fc2 = Fc2()
    seller, sell_date = fc2.get_info('8720511')
    print(seller + ' [' + str(sell_date) + ']')
