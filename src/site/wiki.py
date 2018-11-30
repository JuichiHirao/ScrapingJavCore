import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
from bs4 import BeautifulSoup
from javcore import db
from javcore import data


class WikiSearch:

    def __init__(self):
        # http://sougouwiki.com/d/%C9%F1%A5%EF%A5%A4%A5%D5%28601%A1%C1%29

        # self.main_url = 'http://sougouwiki.com/search?keywords=HIGH-040'
        self.search_url = 'http://sougouwiki.com/search?keywords='
        self.opener = urllib.request.build_opener()
        self.opener.addheaders = [('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]

        self.options = Options()
        self.options.add_argument('--headless')

        self.jav_dao = db.jav.JavDao()
        self.import_dao = db.import_dao.ImportDao()

    def __get_info_from_chrome(self, product_number):
        self.driver = webdriver.Chrome(chrome_options=self.options, executable_path='c:\\SHARE\\chromedriver.exe')

        # print(self.main_url + product_number)
        self.driver.get(self.main_url + product_number)

        sleep(1)

        sell_date = ''
        seller = ''
        for main_info in self.driver.find_elements_by_css_selector('.main_info_block'):
            sleep(1)
            block_text = main_info.text
            # print(main_info.text)
            seller, sell_date = self.__parse_lines(block_text.splitlines())

        self.driver.close()

        return seller, sell_date

    def __parse_lines(self, lines):
        is_date = False
        is_seller = False
        for line in lines:
            if is_date:
                sell_date = line.strip()
                is_date = False
            if is_seller:
                seller = line.strip()
                is_seller = False

            if len(line.strip()) <= 0:
                continue
            if line.strip() == '販売日':
                is_date = True
            if line.strip() == '販売者':
                is_seller = True

        return seller, sell_date

    def __get_info(self, product_number):

        url = self.search_url + product_number

        urllib.request.install_opener(self.opener)
        with urllib.request.urlopen(url) as response:
            html = response.read()
            html_soup = BeautifulSoup(html, "html.parser")
            # print(html_soup)
            result_box = html_soup.find('div', class_='result-box')
            print(len(result_box))

            p_title = result_box.find('p', class_='title').text
            print(p_title)

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

                print('\n'.join(wiki_list))
            else:
                print(len(wikis))

        urllib.request.urlcleanup()

        return ''

    def get_info(self, product_number):

        try:
            return self.__get_info(product_number)
            # return self.__get_info_from_chrome(product_number)
        except:
            # return self.__get_info(product_number)
            return '', ''
            # return self.__get_info_from_chrome(product_number)

    def execute(self):

        jav = data.JavData()
        javs = self.jav_dao.get_where_agreement('WHERE id = 1384')
        for jav in javs:
            print(jav.productNumber)

        self.get_info(jav.productNumber)


if __name__ == '__main__':
    wiki = WikiSearch()
    # wiki.get_info('TEST')
    wiki.execute()
