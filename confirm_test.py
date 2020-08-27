import re
from src import common
from src import data
from src import site
from bs4 import BeautifulSoup
import requests
from src import tool

class SiteInfoGetter:

    def __init__(self):

        url = 'https://avwikich.com/?p=172538'
        # url = 'https://avwikich.com/?cat=7062'
        response = requests.get(url)
        html = response.text
        html_soup = BeautifulSoup(html, 'html.parser')
        jav = data.JavData()
        jav.productNumber = 'MMGH-281'
        # jav.productNumber = 'HUNTA-827'
        site_data = self.__get_info_avwikich(jav, html_soup)
        if site_data is not None:
            site_data.print()

    def __get_info_avwikich(self, jav: data.JavData = None, html_soup: BeautifulSoup = None):

        site_data = self.__get_info_avwikich_p1(jav, html_soup)

        if site_data is not None:
            return site_data

        site_data = self.__get_info_avwikich_p2(jav, html_soup)

        if site_data is not None:
            return site_data

    def __get_info_avwikich_p2(self, jav: data.JavData = None, html_soup: BeautifulSoup = None):

        site_data = data.SiteData()
        div_the_content_list = html_soup.findAll('div', id='the-content')

        re_jav_product_number = re.sub('^[0-9]{3}', '', jav.productNumber.replace('-', '[0]{0,4}')).lower()
        print(re_jav_product_number)
        for div_the_content in div_the_content_list:

            site_data = data.SiteData()
            product_number = ''
            if div_the_content is not None:
                p_c = div_the_content.find('p')
                span_c = div_the_content.find('span')
                # print(span_c.text)
                p_list = p_c.text.split('\n')
                # print(p_list)
                for line_data in p_list:
                    if '出演女優名' in line_data:
                        site_data.actress = re.sub('出演女優名\(名前\)：', '', line_data)
                    if '配信開始日' in line_data:
                        site_data.streamDate = re.sub('配信開始日：', '', line_data)
                    if '品番' in line_data:
                        product_number = re.sub('品番：', '', line_data)

                # print('{} {} {}'.format(product_number, site_data.actress, site_data.streamDate))
                # print(p_c.text)

            # print(jav_product_number)
            if len(product_number) > 0:
                if re.search(re_jav_product_number, product_number.lower()):
                    break
                else:
                    site_data = None
            else:
                site_data = None

        return site_data

    def __get_info_avwikich_p1(self, jav: data.JavData = None, html_soup: BeautifulSoup = None):

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
                    # site_data.actress = m.group()
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

        if is_match is False:
            site_data = None

        return site_data


if __name__ == "__main__":
    getter = SiteInfoGetter()
