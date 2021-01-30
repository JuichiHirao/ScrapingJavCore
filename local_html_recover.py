import os
from time import sleep
from datetime import datetime
from src import db
from src import data
from src import tool
from src import common
from src import site
from bs4 import BeautifulSoup
from mysql.connector.errors import DataError
from selenium.common.exceptions import WebDriverException
import urllib
import shutil
import socket
import traceback
import sys
import re


class EntryRegisterJav:

    def __init__(self):

        self.jav_dao = db.jav.JavDao()
        self.maker_dao = db.maker.MakerDao()
        self.makers = self.maker_dao.get_all()

        self.err_list = []

        self.p_number_tool = tool.p_number.ProductNumber()
        self.env = common.Environment(True)
        self.driver = self.env.get_driver()
        # self.store_path = 'C:\mydata\jav-save\201120-2'
        self.store_path = 'C:\mydata\jav-save'
        self.html_save_path = 'C:\mydata'

        self.parser = common.AutoMakerParser(maker_dao=self.maker_dao)

        self.site_getter = None
        self.site_collect = None
        try:
            self.site_collect = site.SiteInfoCollect()
            self.site_collect.initialize()

            self.site_getter = site.SiteInfoGetter(site_collect=self.site_collect, is_debug=True)
        except:
            print(sys.exc_info())
            exit(-1)

        self.recover = tool.recover.Recover(site_collect=self.site_collect, makers=self.makers)

    def __download_image(self, driver, link):

        thumbnail_url = ''
        try:
            image_id = driver.find_element_by_id('image')
        except:
            image_id = driver.find_element_by_tag_name('img')

        if image_id is not None:
            thumbnail_url = image_id.get_attribute('src')
        else:
            return None

        filename = link[link.rfind("/") + 1:]
        pathname = os.path.join(self.store_path, filename)
        if os.path.isfile(pathname):
            now_date = datetime.now().strftime('%Y-%m-%d-%H%M%S')
            pathname = os.path.join(self.store_path, now_date + '_' + filename)
        print('    img_th ' + filename + ' ' + thumbnail_url)
        try:
            # urllib.request.urlretrieve(thumbnail_url, pathname)
            data = urllib.request.urlopen(thumbnail_url, timeout=10).read()
            with open(pathname, mode="wb") as f:
                f.write(data)
        except socket.timeout as err:
            # self.slack_api.post('collect_jav 263L timeout error {}'.format(thumbnail_url), '@javscraping')
            print('socket.timeout download_image')
            print(str(err))

        return filename

    def __download_thumbnails(self, links):

        arr_dl_files = []
        for link in links:
            try:
                self.driver.get(link)
            except WebDriverException as e:
                sleep(10)
                continue

            # <a style="color: blue; font-size: 40px; text-decoration: underline; cursor: pointer;" class="continue">Continue to your image</a>
            try:
                sleep(3)
                self.driver.find_element_by_class_name('continue').click()
                sleep(3)

                self.driver.switch_to.window(self.driver.window_handles[1])
                sleep(5)
                thumbnail_file = self.__download_image(self.driver, link)
                if thumbnail_file is not None:
                    self.driver.close()  # 遷移先のウィンドウを閉じる。特に必要なければ記述の必要なし
                    arr_dl_files.append(thumbnail_file)
                    all_handles = self.driver.window_handles
                    for win in all_handles:
                        print('  close after switch window ' + str(win))
                        self.driver.switch_to.window(win)
                        break
                else:
                    all_handles = self.driver.window_handles

                    for win in all_handles:
                        print('  win ' + str(win))
                        self.driver.switch_to.window(win)
                        dl_filename = self.__download_image(self.driver, link)
                        arr_dl_files.append(dl_filename)
                        break

            except:
                # print(traceback.format_exc())
                try:
                    print('  not popup page')
                    dl_filename = self.__download_image(self.driver, link)
                    arr_dl_files.append(dl_filename)
                    break

                except:
                    print('  except thumbnail file 404 not found')

        is_download = True

        for filename in arr_dl_files:
            pathname = os.path.join(self.store_path, filename)
            if not os.path.exists(pathname):
                is_download = False
                break

        dl_filenames = ''
        if is_download:
            dl_filenames = ' '.join(arr_dl_files)

        return dl_filenames

    def __get_target_page_list(self):
        start_page = 'Maddawg JAV.html'
        next_page = 'Maddawg JAV - page {}.html'
        html_file_list = []
        html_save_path = 'C:\mydata'

        for idx in range(30):
            if idx == 0:
                page_filename = os.path.join(html_save_path, start_page)
            else:
                page_filename = os.path.join(html_save_path, next_page.format(idx+1))

            if os.path.isfile(page_filename):
                html_file_list.append(page_filename)

        # print(html_file_list)

        return html_file_list

    def __get_img_file(self, img_tag):
        dest_pathname = ''
        filename = ''
        pathname = ''
        if img_tag is None:
            return filename, dest_pathname

        if 'src' in img_tag:
            img_src = img_tag['src']
            if img_src is not None:
                filename = img_tag['src']
            else:
                print('not found src img_tag')
        else:
            m_src_jpg = re.search("src=\".*(jpg|png)\"", str(img_tag))
            if m_src_jpg:
                filename = m_src_jpg.group().replace('src="', '').replace('"', '')
            else:
                print('src key not found error  img_tag {}'.format(img_tag))

        if len(filename) > 0:
            pathname = os.path.join(self.html_save_path, filename)
            if not os.path.exists(pathname):
                print('not exist file {}'.format(filename))
                pathname = ''
            else:
                filename = os.path.basename(pathname)

        if len(pathname) > 0:
            dest_pathname = os.path.join(self.store_path, filename)

        return pathname, dest_pathname, filename

    def register_page(self):

        html_file_list = self.__get_target_page_list()

        for html_pathname in html_file_list:
            # html_pathname = os.path.join(html_save_path, html_file)
            self.__scraping_execute(html_pathname)

    def __scraping_execute(self, html_pathname):

        # print('\n\n\n' + html_pathname + '\n\n\n')
        soup = BeautifulSoup(open(html_pathname, encoding='utf-8'), 'html.parser')

        hentry_list = soup.find_all('div', class_='hentry')
        print('{} {}'.format(len(hentry_list), html_pathname))

        p_tool = tool.p_number.ProductNumber(is_log_print=True)
        for entry in hentry_list:
            title = ''
            for h2 in entry.find('h2'):
                title = h2.text
                # url = h2['href']
                break

            jav_id = self.jav_dao.get_exist_id(title)
            # title_exist = self.jav_dao.is_exist(jav.title)

            if jav_id <= 0:
                print('[{}]のデータなし'.format(title))
                continue

            javs = self.jav_dao.get_where_agreement('WHERE id = {}'.format(jav_id))

            if len(javs) <= 0:
                print('jav.id[{}]のデータなし'.format(javs))
                continue

            elif len(javs) > 1:
                print('jav.id[{}]の複数{}個データ存在'.format(jav_id, len(javs)))
                continue

            jav = javs[0]

            img_tag = ''
            filename = ''
            if jav.package is None or len(jav.package) <= 0:
                print('package start [{}] {}'.format(jav.id, jav.title))
                # package ファイルをローカルからローカルへコピー
                div_entry = entry.find('div', class_='entry')
                img_tag = div_entry.find('img')
                src_pathname, dest_pathname, filename = self.__get_img_file(img_tag)
                if len(dest_pathname) > 0:
                    shutil.copy2(src_pathname, dest_pathname)
                    self.jav_dao.update_package(jav.id, filename)

                if len(filename) <= 0:
                    message = '[{}] package 再取得失敗 {}\n    {}'.format(jav.id, jav.title, img_tag)
                    print(message)
                    self.err_list.append(message)

            if jav.thumbnail is None or len(jav.thumbnail) <= 0:
                print('thubmnail start [{}] {}'.format(jav.id, jav.title))
                # thumbnail ファイルをネットから取得
                a_list = entry.find_all('a')
                thumbnail_files = []
                thumbnail_link = ''
                for a in a_list:
                    if 'https://pixhost' in a['href']:
                        thumbnail_link = a['href']
                        links = []
                        print(thumbnail_link)
                        links.append(thumbnail_link)
                        thumbnail_files = self.__download_thumbnails(links)
                        if len(thumbnail_files) > 0:
                            if jav.id > 0:
                                self.jav_dao.update_thumbnail(jav.id, thumbnail_files)

                if len(thumbnail_files) <= 0:
                    self.err_list.append('[{}] thubmanil再取得失敗 {}\n    {}'.format(jav.id, jav.title, thumbnail_link))

        for err in self.err_list:
            print(err)


if __name__ == '__main__':
    entry_register = EntryRegisterJav()
    entry_register.register_page()
    # package_file = 'C:\mydata\\' + './Maddawg JAV - page 4_files/172406389_230oretd-796.jpg'
    # print(os.path.isfile(package_file))

