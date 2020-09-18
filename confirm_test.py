import re
import urllib.request
import urllib.error
from src import common
from src import data
from src.site import mgs
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from src import tool

class SiteInfoGetter:

    def __init__(self):

        url = 'https://www.roguelibrarian.com/orenoshirouto'
        # url = 'https://av-wiki.net/fanza-shirouto/sqb/'
        # url = 'http://sougouwiki.com/d/S-Cute%20Girls%208'
        # url = 'https://av-wiki.net/fanza-shirouto/szdr/'
        # url = 'https://av-wiki.net/fanza-shirouto/sqb/'
        # url = 'https://avwikich.com/?p=172538'
        # url = 'https://avwikich.com/?cat=7062'
        response = requests.get(url)
        response.raise_for_status()
        response.encoding = 'utf_8'  # 文字コード
        html = response.text
        html_soup = BeautifulSoup(html, 'html.parser')
        jav = data.JavData()
        jav.productNumber = '230OREC-561'
        # jav.productNumber = '742_rui_03'
        # jav.productNumber = '380SQB-033'
        # jav.productNumber = '448SZDR-003'
        # jav.productNumber = '742'
        # jav.productNumber = 'HUNTA-827'
        # site_data = self.__get_info_avwikich(jav, html_soup)
        site_data = self.__get_info_roguelibrarian(jav, html_soup)
        if site_data is not None:
            site_data.print()

    def __get_info_roguelibrarian(self, jav: data.JavData = None, html_soup: BeautifulSoup = None):

        site_data = data.SiteData()

        contents_list = html_soup.findAll('article', class_='hentry')

        is_match = False
        for idx, div_c in enumerate(contents_list):
            product_c = div_c.find('h2')
            if product_c is None:
                break

            if jav.productNumber in product_c.text.strip():
                a_c = div_c.find('a', class_='actress_meta_box')
                # print(div_c)
                citi_link = div_c.find('blockquote', class_='entry-title')
                print(citi_link['cite'])
                if 'product_detail' in citi_link['cite']:
                    site_data = mgs.mgs.get_info(jav.productNumber)
                site_data.actress = a_c.text
                is_match = True

            if is_match:
                break

        if is_match is False:
            page_c = html_soup.find('div', class_='pager_right')
            site_data = None
            if page_c is not None:
                next_page_c = page_c.find('a')
                with urllib.request.urlopen(next_page_c['href']) as response:
                    html = response.read()
                    html_soup = BeautifulSoup(html, 'html.parser')
                    site_data = self.__get_info_roguelibrarian(jav, html_soup)

        return site_data

    # def __get_info_scute(self):
    def __get_info_sougouwiki(self, jav: data.JavData = None, html_soup: BeautifulSoup = None):

        site_data = data.SiteData()

        # main_table = html_soup.find('table', class_='edit')
        main_tables = html_soup.findAll('table')
        td_data_list = ['', '', '', '', '']  # 0 pNum, 1 img, 2 title, 3 a_name, 4 date
        is_match = False
        for table in main_tables:
            # td_data_list = [] # 0 pNum, 1 img, 2 title, 3 a_name, 4 date
            tr_list = table.findAll('tr')
            for tr in tr_list:
                td_list = tr.findAll('td', recursive=False)
                # print(tr)
                # a_link = tr.find('a', class_='outlink')
                # print(a_link['href'])

                idx = 0
                for td in td_list:
                    a_link = td.find('a', class_='outlink')
                    if a_link is not None:
                        href_link = a_link['href']
                        if 'jpg' not in href_link:
                            if 'www.s-cute.com' in href_link:
                                print(href_link)
                    else:
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
                    # print(str(td_data_list))
                    site_data.actress = td_data_list[3]
                    site_data.streamDate = td_data_list[4]
                    break
                else:
                    site_data.actress = ''

            if is_match:
                break

        return site_data


if __name__ == "__main__":
    getter = SiteInfoGetter()
