import re
import urllib.request
from bs4 import BeautifulSoup
from .. import common
from .. import db
from .. import data


class Hey:

    def __init__(self):
        self.main_url = 'http://www.heydouga.com/moviepages/'
        self.suffix_url = 'index.html'
        self.opener = urllib.request.build_opener()
        self.opener.addheaders = [('User-Agent',
                                   'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]

        self.env = common.Environment()
        self.driver = self.env.get_driver()
        self.import_dao = db.import_dao.ImportDao()

    def get_info(self, product_number):

        site_data = None
        if re.search('[0-9]{4}_[0-9]{3,4}',product_number):
            arr_p_num = product_number.split('_')

            url = self.main_url + arr_p_num[0] + '/' + arr_p_num[1] + '/index.html'

            urllib.request.install_opener(self.opener)

            try:
                with urllib.request.urlopen(url) as response:
                    html = response.read()
                    html_soup = BeautifulSoup(html, "html.parser")
                    movie_info = html_soup.find('div', id='movie-info')
                    # print(movie_info.text)
                    site_data = data.SiteData()
                    for line in movie_info.text.splitlines():
                        if re.search('配信日', line):
                            site_data.streamDate = re.sub('配信日：', '', line).strip()
                        if re.search('提供元', line):
                            site_data.maker = re.sub('提供元：|[(（] 公式サイト [)）]', '', line).strip()
                        if re.search('主演', line):
                            site_data.actress = re.sub('主演：', '', line).strip()
                        if re.search('動画再生時間', line):
                            site_data.duration = re.sub('動画再生時間：', '', line).strip()
                        if re.search('ファイル容量', line):
                            site_data.fileSize = re.sub('ファイル容量：', '', line)
                        if re.search('画面サイズ', line):
                            site_data.screenSize = re.sub('画面サイズ：', '', line)
                    # site_data.print()
            except urllib.error.HTTPError as err:
                print('HTTPError [' + str(err.code) + ']')

        else:
            print('not found')

            # seller, sell_date = self.__parse_lines(block_text.splitlines())

        urllib.request.urlcleanup()

        return site_data

