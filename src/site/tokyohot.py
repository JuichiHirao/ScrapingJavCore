import re
import urllib.request
from bs4 import BeautifulSoup
from .. import common
from .. import db
from .. import data


class Tokyohot:

    def __init__(self):
        # self.main_url = 'https://my.tokyo-hot.com/'
        self.main_url = 'https://www.tokyo-hot.com/'
        self.opener = urllib.request.build_opener()
        self.opener.addheaders = [('User-Agent',
                                   'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]

        self.env = common.Environment()
        self.driver = self.env.get_driver()
        self.import_dao = db.import_dao.ImportDao()

    def get_info(self, product_number: str=''):

        site_data = None

        url = '{}product/{}/'.format(self.main_url, product_number.lower())
        urllib.request.install_opener(self.opener)

        try:
            with urllib.request.urlopen(url) as response:
                html = response.read()
                html_soup = BeautifulSoup(html, "html.parser")
                contents_info = html_soup.find('dl', class_='info')
                site_data = data.SiteData()
                key = ''
                for dtdd in contents_info.find_all(['dt', 'dd']):
                    if dtdd.name == 'dt':
                        if '配信開始日' in dtdd.text or 'release date' in dtdd.text.lower():
                            key = 'streamDate'
                            continue
                        if 'レーベル' in dtdd.text or 'label' in dtdd.text.lower():
                            key = 'label'
                            continue
                        if '収録時間' in dtdd.text or 'duration' in dtdd.text.lower():
                            key = 'duration'
                            continue
                    if dtdd.name == 'dd':
                        if key == 'streamDate':
                            site_data.streamDate = dtdd.text
                        if key == 'label':
                            site_data.maker = dtdd.text
                        if key == 'duration':
                            site_data.duration = dtdd.text
                        key = ''

        except urllib.error.HTTPError as err:
            print('HTTPError [' + str(err.code) + ']')
        except AttributeError as err:
            print('NoneType Error')

        urllib.request.urlcleanup()

        return site_data
