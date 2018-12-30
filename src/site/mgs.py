import re
import urllib.request
from selenium.common import exceptions
from .. import common
from .. import db
from .. import data


class Mgs:

    def __init__(self):
        self.main_url = 'https://www.mgstage.com/product/product_detail/'
        self.opener = urllib.request.build_opener()
        self.opener.addheaders = [('User-Agent',
                                   'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]

        self.env = common.Environment()
        self.driver = self.env.get_driver()
        self.import_dao = db.import_dao.ImportDao()

    def __get_info_from_chrome(self, product_number):

        self.driver.get(self.main_url + product_number + '/')

        detail = ''
        sell_date = ''
        h2 = None
        try:
            h2 = self.driver.find_element_by_tag_name('h2')
        except exceptions.NoSuchElementException:
            print('h2 tag not found exceptions.NoSuchElementException')

        if h2 is None:
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

        site_data = data.SiteData()
        if h1 != None:
            site_data.title = h1.text

        # 存在しない品番の場合は、forをそのままスルー、空文字でリターンされる
        for tr_tag in self.driver.find_elements_by_tag_name('tr'):

            try:
                th_tag = tr_tag.find_element_by_tag_name('th')
            except:
                th_tag = None

            if not th_tag:
                continue

            if re.search('出演', th_tag.text):
                td_tag = tr_tag.find_element_by_tag_name('td')
                site_data.actress = td_tag.text
                # detail += td_tag.text + '、'
            if re.search('メーカー', th_tag.text):
                td_tag = tr_tag.find_element_by_tag_name('td')
                site_data.maker = td_tag.text
                # detail += td_tag.text + '、'
            if re.search('収録時間', th_tag.text):
                td_tag = tr_tag.find_element_by_tag_name('td')
                site_data.duration = td_tag.text
            if re.search('品番', th_tag.text):
                td_tag = tr_tag.find_element_by_tag_name('td')
                site_data.productNumber = td_tag.text
            if re.search('配信開始日', th_tag.text):
                td_tag = tr_tag.find_element_by_tag_name('td')
                site_data.streamDate = td_tag.text
            if re.search('商品発売日', th_tag.text):
                td_tag = tr_tag.find_element_by_tag_name('td')
                site_data.sellDate = td_tag.text
            if re.search('シリーズ', th_tag.text):
                td_tag = tr_tag.find_element_by_tag_name('td')
                site_data.series = td_tag.text
            if re.search('レーベル', th_tag.text):
                td_tag = tr_tag.find_element_by_tag_name('td')
                site_data.label = td_tag.text

        # detail += title

        return site_data

    def get_info(self, product_number):

        return self.__get_info_from_chrome(product_number)

    def exist_product_number(self, product_number):

        self.driver.get(self.main_url + product_number + '/')

        h2 = None
        try:
            h2 = self.driver.find_element_by_tag_name('h2')
        except exceptions.NoSuchElementException:
            print('h2 tag not found exceptions.NoSuchElementException')

        if h2 is None:
            print('h2 tag none')
            return False

        if h2.text == '年齢認証':
            over18yes = self.driver.find_element_by_tag_name('li')
            # over18yes = self.driver.find_element_by_id('id')
            over18yes.click()

        try:
            h1 = self.driver.find_element_by_css_selector('.tag')
        except exceptions.NoSuchElementException:
            print('h1 tag not found exceptions.NoSuchElementException')
            return False

        # 存在しない品番の場合は、forをそのままスルー、空文字でリターンされる
        for tr_tag in self.driver.find_elements_by_tag_name('tr'):
            return True

        return False

    def test_execute(self):

        imports = self.import_dao.get_all()
        if len(imports) > 0:
            for one_data in imports:
                detail, sell_date = self.get_info(one_data.productNumber)
                if len(sell_date) > 0:
                    print(one_data.copy_text)
                    print(detail)
                    print('')
                    self.import_dao.update_detail_and_sell_date(detail, sell_date, one_data.id)


if __name__ == '__main__':

    mgs = Mgs()
    # detail, sell_date = mgs.get_info('277DCV-093')
    detail, sell_date = mgs.test_execute()
    # print(' [' + str(sell_date) + '] ' + detail)

