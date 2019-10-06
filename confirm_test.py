import re
from src import common
from src import data
from bs4 import BeautifulSoup
import requests

'''
match_maker = data.MakerData()
match_maker.matchName = 'S1 NO.1 STYLE'
match_maker.matchStr = 'SSNI'
match_maker.matchProductNumber = ''
copy_text = common.CopyText()
# title = copy_text.get_title('[FHD6m]ssni-391 隣に住む引きこもりの幼馴染に私、毎日アニコスを着させられて… 夢乃あいか', 'SSNI-391')
title = copy_text.get_title('[FHD]ssni-391 隣に住む引きこもりの幼馴染に私、毎日アニコスを着させられて… 夢乃あいか', 'SSNI-391')
print(title)
'''

env = common.Environment()

# print(' [' + env.get_exist_image_path('102044785_0016cbb5.jpg') + ']')
print(' [' + env.get_exist_image_path('4785_0016cbb5.jpg') + ']')

url = 'https://shecool.net/av-wiki/fanza-shirouto/276kitaike-av-actress-name-301-400/'
site_data = data.SiteData()

response = requests.get(url)
html = response.text
html_soup = BeautifulSoup(html, 'html.parser')

contents_list = html_soup.findAll('div', class_='s-contents')
# print('contents_list ' + str(len(contents_list)))

match_sell_date = '[12][0][0-9][0-9][-/][0-1][0-9][-/][0-3][0-9]'
is_match = False
for idx, div_c in enumerate(contents_list):
    p_c = div_c.find('p')
    # a_name = div_c.find('a')
    # if a_name is not None:
    #     actress = a_name.text
    #     print('  a_text ' + str(a_name_text.text))

    # str_p = p_c.text
    """
    0  [ <span class="important-bold">女優名：</span>]
    1  [ 香坂澪]
    2  [ <br/>]
    3  [ <span class="small">澪　33歳<br/>品番：<span class="fanza-num">kitaike301</span> – <span class="mgs-num">
         <a href="https://www.mgstage.com/product/product_detail/276KITAIKE-347/?aff=QTWJYS6BP24YCHBPG2PDC83284" rel="nofollow" target="_blank">276KITAIKE-347</a></span>
         <br/>配信開始日：2018-09-14</span>]
    """
    if '276KITAIKE-401' not in p_c.text:
        continue

    # print(p_c.text)
    actress = ''
    streamDate = None
    for idx, elem in enumerate(p_c.childGenerator()):
        if idx == 1:
            actress = str(elem)
        if idx == 3:
            str_elem = str(elem)
            # span_c = elem.findAll('span')
            if re.search('[12][0][0-9][0-9][-/][0-1][0-9][-/][0-3][0-9]', str_elem):
                m = re.search(match_sell_date, str_elem)
                # print('avwiki match sell_date ' + str(m.group()))
                streamDate = m.group()
                break
    # print(p_c.text)
    # print("title     [{}]".format(title))
    print("actress   [{}]".format(actress))
    print("stremDate [{}]".format(streamDate))
    """
    span_c = div_c.findAll('span')
    for span_text in span_c:
        print('span ' + span_text.text)
        if '女優' in span_text.text:
            actress_name = re.sub('女優名.*：', '', span_text.text)
            print('actress ' + actress_name)
        # print('  span_text ' + span_text.text)
        if re.search('[12][0][0-9][0-9][-/][0-1][0-9][-/][0-3][0-9]', span_text.text):
            m = re.search(match_sell_date, span_text.text)
            # print('avwiki match sell_date ' + str(m.group()))
            streamDate = m.group()
    """

# print(actress)
# print(streamDate)

