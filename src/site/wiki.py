import urllib.request
from bs4 import BeautifulSoup
from javcore import db


class SougouWiki:

    def __init__(self):

        self.search_url = 'http://sougouwiki.com/search?keywords='

        self.opener = urllib.request.build_opener()
        self.opener.addheaders = [('User-Agent',
                                        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]

        self.jav_dao = db.jav.JavDao()
        self.import_dao = db.import_dao.ImportDao()

    def __get_info(self, product_number):

        url = self.search_url + product_number

        result_search = ''
        urllib.request.install_opener(self.opener)
        with urllib.request.urlopen(url) as response:
            html = response.read()
            html_soup = BeautifulSoup(html, "html.parser")
            result_box = html_soup.find('div', class_='result-box')
            # print(len(result_box))

            # p_title = result_box.find('p', class_='title').text
            # print(p_title)

            wikis = result_box.findAll('h3', class_='keyword')
            len_wikis = len(wikis)

            if len_wikis > 0:
                wiki_list = []
                for idx, wiki in enumerate(wikis):
                    a = wiki.find('a')
                    # print(str(idx), str(a))
                    url = a['href']
                    wiki_list.append(a.text + ' ' + url)
                    # print(a.text + ' ' + url)

                result_search = '\n'.join(wiki_list)

        urllib.request.urlcleanup()

        return result_search

    def search(self, product_number):

        return self.__get_info(product_number)

    def test_execute(self):

        # javs = self.jav_dao.get_where_agreement('WHERE id = 1384')

        # result = self.search(javs[0].productNumber)
        # self.jav_dao.update_search_result(result, javs[0].id)

        imports = self.import_dao.get_all()
        if len(imports) > 0:
            for one_data in imports:
                result = self.search(one_data.productNumber)
                if len(result) > 0:
                    print(one_data.copy_text)
                    print(result)
                    print('')
                    self.import_dao.update_search_result(result, one_data.id)


if __name__ == '__main__':

    wiki = SougouWiki()
    wiki.test_execute()
