import re
import urllib.request
import urllib.error
import urllib.parse
from selenium.common import exceptions
from bs4 import BeautifulSoup


class Fanza:

    def __init__(self):
        self.main_url = 'https://www.google.com/search?q='
        # self.url_suffix = '+fanza+av'
        self.url_suffix = '+wiki+av'
        self.opener = urllib.request.build_opener()
        self.opener.addheaders = [('User-Agent',
                                   'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]

    def get_info_google(self, p_number):

        site_data = None
        url = self.main_url + p_number + self.url_suffix

        split_p_number = p_number.split('-')
        urllib.request.install_opener(self.opener)

        try:
            with urllib.request.urlopen(url) as response:
                html = response.read()
                # html_pathname = 'google_result.html'
                # with open(html_pathname, mode='wb') as f:
                #     f.write(html.decode('utf-8'))
                    # f.write(html)
                # google_result_soup = BeautifulSoup(open(html_pathname, encoding='utf-8'), "html.parser")
                google_result_soup = BeautifulSoup(html, "html.parser")
                # div_r_list = google_result_soup.findAll('div')
                div_search = google_result_soup.select('#search')
                # div_list = div_search[0].findAll('div', class_='rc')
                div_list = div_search[0].findAll('div', class_='rc')
                # div_list = div_search[0].findAll('div')
                # for div in div_list:
                #     print(div)
                for div in div_list:
                    link = div.find('a')
                    if link is None:
                        continue
                    href = link['href']
                    if href is not None:
                        print(link['href'])
                # div_r_list = google_result_soup.findAll('div')
                # for idx, div_r in enumerate(div_r_list):
                #     print(div_r)


                '''
                for idx, div_r in enumerate(div_r_list):
                    print(div_r)
                    a_div_r = div_r.find('a')
                    url = a_div_r['href']

                    # site_data = self.__get_and_check_site_data(p_number, split_p_number, url)

                    # if site_data is not None:
                    #     break

                    if idx > 3:
                        break
                '''

        except AttributeError as aerr:
            print(str(aerr))
            print('error [' + url + ']')

        except urllib.error.URLError as uerr:
            print(str(uerr))
            print('error [' + url + ']')

        return site_data


if __name__ == "__main__":
    getter = Fanza()
    getter.get_info_google('HONB-190')
