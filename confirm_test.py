import re
import urllib.request
import urllib.error
from src import common
from src import data
from src import site
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
        # jav.productNumber = '230OREC-561'
        # jav.productNumber = '742_rui_03'
        # jav.productNumber = '380SQB-033'
        # jav.productNumber = '448SZDR-003'
        # jav.productNumber = '742'
        # jav.productNumber = 'HUNTA-827'
        # site_data = self.__get_info_avwikich(jav, html_soup)
        site_data = self.__get_info_avwiki_net(jav, html_soup)
        if site_data is not None:
            site_data.print()

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

    def __get_info_avwiki_net(self, jav: data.JavData = None, html_soup: BeautifulSoup = None):

        site_data = data.SiteData()

        link_wrap_list = html_soup.findAll('div', class_='link-wrap')
        td_data_list = ['', '', '', '', ''] # 0 pNum, 1 img, 2 title, 3 a_name, 4 date
        is_match = False
        re_jav_product_number = re.sub('^[0-9]{3}', '', jav.productNumber.replace('-', '[0]{0,4}')).lower()
        # print(re_jav_product_number)
        product_number = ''
        is_match = False
        for link_wrap in link_wrap_list:
            site_data = data.SiteData()

            li_actress = link_wrap.find('li', class_='actress-name')
            if li_actress is not None:
                # print(li_actress.text)
                a_actress = li_actress.find('a')
                if a_actress is not None:
                    site_data.actress = a_actress.text

            li_haishin_date = link_wrap.find('li', class_='haishin-date')
            if li_haishin_date is not None:
                # print(li_haishin_date.text)
                stream_str_date = datetime.strptime(li_haishin_date.text, '%Y年%m月%d日')
                site_data.streamDate = datetime.strftime(stream_str_date, '%Y-%m-%d')

            li_fanza_num = link_wrap.find('li', class_='fanza-num')
            if li_fanza_num is not None:
                product_number = li_fanza_num.text

            # print(li_actress.encode('Shift-JIS', errors='ignore'))
            # print(li_actress.encode('UTF-8', errors='ignore'))
            # print(li_actress.encode('ISO-2022-JP', errors='ignore'))
            # print(li_actress.encode('CP932', errors='ignore'))
            if len(product_number) > 0:
                if re.search(re_jav_product_number, product_number.lower()):
                    is_match = True
                    print(li_actress)
                    break
                else:
                    site_data = None
            else:
                site_data = None
            # site_data.actress = ''

            # if is_match:
            #     break

        if is_match is False:
            next_page_c = html_soup.find('a', class_='next page-numbers')
            site_data = None
            if next_page_c is not None:
                response = requests.get(next_page_c['href'])
                response.raise_for_status()
                response.encoding = 'utf_8'  # 文字コード
                html = response.text
                html_soup = BeautifulSoup(html, 'html.parser')
                site_data = self.__get_info_avwiki_net(jav, html_soup)

        return site_data

    def __get_info_sougouwiki(self, jav: data.JavData = None, html_soup: BeautifulSoup = None):

        site_data = data.SiteData()

        # main_table = html_soup.find('table', class_='edit')
        main_tables = html_soup.findAll('table')
        td_data_list = ['', '', '', '', ''] # 0 pNum, 1 img, 2 title, 3 a_name, 4 date
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
