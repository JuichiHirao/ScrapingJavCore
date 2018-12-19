import re
import urllib.request
from javcore import common
from selenium.common import exceptions


class Mgs:

    def __init__(self):
        self.main_url = 'https://www.mgstage.com/product/product_detail/'
        self.opener = urllib.request.build_opener()
        self.opener.addheaders = [('User-Agent',
                                   'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]

        self.env = common.Environment()
        self.driver = self.env.get_driver()

    def __get_info_from_chrome(self, product_number):

        self.driver.get(self.main_url + product_number + '/')

        detail = ''
        sell_date = ''
        h2 = None
        try:
            h2 = self.driver.find_element_by_tag_name('h2')
        except exceptions.NoSuchElementException:
            print('h2 tag not found exceptions.NoSuchElementException')

        if h2 == None:
            print('h2 tag none')
            return detail, sell_date

        if h2.text == '年齢認証':
            over18yes = self.driver.find_element_by_tag_name('li')
            # over18yes = self.driver.find_element_by_id('id')
            over18yes.click()

        h1 = None
        try:
            h1 = self.driver.find_element_by_css_selector('.tag')
        except exceptions.NoSuchElementException:
            print('h1 tag not found exceptions.NoSuchElementException')

        title = ''
        if h1 != None:
            title = h1.text

        # 存在しない品番の場合は、forをそのままスルー、空文字でリターンされる
        for tr_tag in self.driver.find_elements_by_tag_name('tr'):

            try:
                th_tag = tr_tag.find_element_by_tag_name('th')
            except:
                th_tag = None

            if not th_tag:
                continue

            if re.search('配信開始日', th_tag.text):
                td_tag = tr_tag.find_element_by_tag_name('td')
                sell_date = td_tag.text
            if re.search('出演', th_tag.text):
                td_tag = tr_tag.find_element_by_tag_name('td')
                detail += td_tag.text + '、'
            if re.search('メーカー', th_tag.text):
                td_tag = tr_tag.find_element_by_tag_name('td')
                detail += td_tag.text + '、'

        detail += title

        return detail, sell_date

    def get_info(self, product_number):

        return self.__get_info_from_chrome(product_number)


if __name__ == '__main__':

    mgs = Mgs()
    detail, sell_date = mgs.get_info('277DCV-093')
    # print(' [' + str(sell_date) + '] ' + detail)

