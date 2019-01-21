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
        for main_info in self.driver.find_elements_by_css_selector('.main_info_block'):
            sleep(1)
            block_text = main_info.text
            # print(main_info.text)
            site_data = self.__get_site_data(block_text.splitlines())

        self.driver.close()

        return site_data

    def __get_site_data(self, lines):

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
            block_text = html_soup.find('div', class_='main_info_block').text

            site_data = self.__get_site_data(block_text.splitlines())

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
