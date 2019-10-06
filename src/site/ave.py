import re
import urllib.request
from datetime import datetime
from bs4 import BeautifulSoup
from .. import common
from .. import db
from .. import data


class Ave:

    def __init__(self):
        self.main_url = 'https://my.tokyo-hot.com/'
        self.opener = urllib.request.build_opener()
        self.opener.addheaders = [('User-Agent',
                                   'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]

        self.env = common.Environment()
        self.driver = self.env.get_driver()
        self.import_dao = db.import_dao.ImportDao()

    def get_info(self, site_url: str=''):

        site_data = None

        urllib.request.install_opener(self.opener)

        try:
            with urllib.request.urlopen(site_url) as response:
                html = response.read()
                html_soup = BeautifulSoup(html, "html.parser")
                contents_info = html_soup.find('div', id='titlebox')
                site_data = data.SiteData()
                idx = 0
                for li in contents_info.find_all('li'):
                    # print('li_span')
                    li_span = li.find('span')
                    li_a = li.find('a')

                    if li_span is not None and li_a is not None:
                        # print('title {} content {}'.format(li_span.text, li_a.text))
                        if 'スタジオ' in li_span.text:
                            site_data.label = li_a.text
                    else:
                        if '発売日' in li.text:
                            # print('sell_date li_text {}'.format(li.text))
                            m_date = re.search('[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}', li.text)
                            if m_date:
                                # print('sell_date2 {}'.format(m_date.group()))
                                m_date_list = m_date.group().split('/')
                                site_data.sellDate = '{}-{}-{}'.format(m_date_list[2]
                                                                       , '{:0>2}'.format(m_date_list[0])
                                                                       , '{:0>2}'.format(m_date_list[1]))
                        if idx == 0:
                            site_data.title = li.text
                        # print('li_text {}'.format(li.text))
                    idx = idx + 1

        except urllib.error.HTTPError as err:
            print('HTTPError [' + str(err.code) + ']')
        except AttributeError as err:
            print('NoneType Error')

        urllib.request.urlcleanup()
        site_data.print()

        return site_data

