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
        self.store_path = 'C:\mydata\jav-save'
        self.html_save_path = 'C:\mydata'

        self.slack_api = tool.slack.SlackApi()
        # self.slack_api.post('test', '@javscraping')

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

        # self.is_check = True
        self.is_check = False

        self.register_count = 0
        self.err_package_count = 0
        self.err_thumbnail_count = 0

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

    def __download_thumbnail(self, link):

        if link is None or len(link) <= 0:
            return False, ''

        try:
            self.driver.get(link)
        except WebDriverException as e:
            sleep(10)
            return

        thumbnail_file = ''
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
                    thumbnail_file = self.__download_image(self.driver, link)
                    break

        except:
            # print(traceback.format_exc())
            try:
                print('  not popup page')
                thumbnail_file = self.__download_image(self.driver, link)
            except:
                print('  except thumbnail file 404 not found')

        is_download = True

        pathname = os.path.join(self.store_path, thumbnail_file)
        if not os.path.exists(pathname):
            is_download = False

        return is_download, thumbnail_file

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

    def register_page(self):

        html_file_list = self.__get_target_page_list()

        for html_pathname in html_file_list:
            # html_pathname = os.path.join(html_save_path, html_file)
            self.__scraping_execute(html_pathname)

        javs = self.jav_dao.get_where_agreement("WHERE is_selection = 0")
        if javs is None:
            javs = []
        message = '未処理 {}件 新規登録 {}件 err package {}件、thumbnail {}件'.format(len(javs), self.register_count
                                                                , self.err_package_count, self.err_thumbnail_count)
        print(message)
        self.slack_api.post(message, '@javscraping')

    def __set_site_info(self, jav, match_maker):

        if jav.isParse2 <= 0:
            return

        site_data = self.site_getter.get_info(jav, match_maker)

        result_search = ''
        detail = ''
        actress_name = ''
        is_selldate_changed = False
        if site_data is None:
            if match_maker.name == 'SITE':
                result_search = self.site_getter.get_wiki(jav, match_maker)

                if len(result_search.strip()) > 0:
                    print('    site result_search [' + result_search + ']')
                    self.jav_dao.update_search_result(result_search.strip(), jav.id)
                else:
                    print('    site result not found ')
            else:
                self.err_list.append('id [' + str(jav.id) + '] site_data is None 【' + jav.title + '】')
        else:
            detail = site_data.get_detail()
            try:
                self.jav_dao.update_detail_and_sell_date(detail, site_data.streamDate, jav.id)
            except DataError as de:
                print(str(de))
                print(traceback.format_exc())

            # site_data = data.SiteData()
            print('    site found [' + detail + ']')
            result_search = self.site_getter.get_wiki(jav, match_maker)
            print('    result_search [' + result_search + ']')

            wiki_detail_data = self.site_getter.get_contents_info(jav, result_search)

            if wiki_detail_data is not None:
                actress_name = wiki_detail_data.actress
                if jav.sellDate is None:
                    if len(wiki_detail_data.streamDate) > 0:
                        print('sell_date ' + wiki_detail_data.streamDate)
                        is_selldate_changed = True
                if len(actress_name) > 0 >= len(jav.actress):
                    print('    change actress [' + actress_name + '] <-- [' + jav.actress + ']')
                    self.jav_dao.update_actress(jav.id, actress_name)

        # FC2 label
        if match_maker is not None and (match_maker.id == 835 or match_maker.id == 255):
            if site_data is not None and jav.label != site_data.maker:
                self.jav_dao.update_maker_label(jav.maker, site_data.maker, jav.id)

        return

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
            m_src_jpg = re.search("src=\".*jpg\"", str(img_tag))
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

    def __scraping_execute(self, html_pathname):

        print('\n\n\n' + html_pathname + '\n\n\n')
        soup = BeautifulSoup(open(html_pathname, encoding='utf-8'), 'html.parser')

        hentry_list = soup.find_all('div', class_='hentry')
        print('{}'.format(len(hentry_list)))

        p_tool = tool.p_number.ProductNumber(is_log_print=True)
        for entry in hentry_list:
            jav = data.JavData()
            for h2 in entry.find('h2'):
                jav.title = h2.text
                jav.url = h2['href']
                # for a in h2.find_all('a'):
                # print(jav.url)
                break

            title_exist = self.jav_dao.is_exist(jav.title)

            is_exist = False
            if title_exist:
                print('title exist ' + jav.title)
                is_exist = True
                # continue

            # if bool("[VR3K]" in jav.title) or bool("【VR】" in jav.title):
            #     continue

            lines = entry.text.splitlines()

            for one in lines:
                if len(one.strip()) <= 0:
                    continue

                if "発売日" in one:
                    str_date = jav.get_date(one)
                    if len(str_date) > 0:
                        jav.sellDate = jav.get_date(one)

                if "出演者" in one:
                    jav.actress = jav.get_text(one)
                if "メーカー" in one:
                    jav.maker = jav.get_text(one)
                if "レーベル" in one:
                    jav.label = jav.get_text(one)

            for span in entry.find_all('div', class_='post-info-top'):
                str_date = span.find('a').text
                str_time = span.find('a')['title']
                # June 29, 2018 7:42 am
                str_datetime = str_date + ' ' + str_time
                jav.postDate = datetime.strptime(str_datetime, '%B %d, %Y %I:%M %p')
                # print(post_date)

            jav.productNumber, match_maker, jav.isParse2 = p_tool.parse(jav, True)
            # jav.productNumber, match_maker, jav.isParse2 = self.p_number_tool.parse(jav, True)
            if jav.isParse2 < 0:
                self.err_list.append('  ' + str(jav.isParse2) + ' [' + jav.productNumber + '] ' + jav.title)

            if bool("[VR3K]" in jav.title) or bool("【VR】" in jav.title):
                self.err_list.append(
                    '  VRなので、対象外に設定 ' + str(jav.isParse2) + ' [' + jav.productNumber + '] ' + jav.title)
                # no_target_cnt = no_target_cnt + 1
                jav.isSelection = -1
            else:
                jav.isSelection = 0

            if match_maker is not None:
                jav.makersId = match_maker.id

            if not self.is_check:
                if not is_exist:
                    self.register_count = self.register_count + 1
                    self.jav_dao.export(jav)
            else:
                print('is_check console output export')

            print(html_pathname + '\n')
            jav.print()

            jav.id = self.jav_dao.get_exist_id(jav.title)
            # package ファイルをローカルからローカルへコピー
            div_entry = entry.find('div', class_='entry')
            # img_tag = div_entry.find('img')
            src_pathname, dest_pathname, filename = self.__get_img_file(div_entry.find('img'))
            print('{} <-- {}\n  {}'.format(dest_pathname, src_pathname, div_entry))
            if len(dest_pathname) > 0:
                if not self.is_check:
                    shutil.copy2(src_pathname, dest_pathname)
                    self.jav_dao.update_package(jav.id, filename)

            if len(dest_pathname) <= 0:
                self.err_package_count = self.err_package_count + 1
                self.err_list.append('[{}] package なし {}'.format(jav.id, jav.title))

            # thumbnail ファイルをネットから取得
            a_list = entry.find_all('a')
            thumbnail_files = []
            for a in a_list:
                if 'https://pixhost' in a['href']:
                    is_download = False
                    thumbnail_file = ''
                    if not self.is_check:
                        is_download, thumbnail_file = self.__download_thumbnail(a['href'])

                    if is_download:
                        thumbnail_files.append(thumbnail_file)

            if len(thumbnail_files) > 0:
                if jav.id > 0:
                    if not self.is_check:
                        files = ' '.join(thumbnail_files)
                        print('thumbnail files [{}]'.format(files))
                        self.jav_dao.update_thumbnail(jav.id, files)
                    else:
                        print('is_check console copy thumbnail {}'.format(thumbnail_files))

            if not self.is_check:
                self.__set_site_info(jav, match_maker)

            if len(thumbnail_files) <= 0:
                self.err_thumbnail_count = self.err_thumbnail_count + 1
                self.err_list.append('[{}] thubmanilなし {}'.format(jav.id, jav.title))

        for err in self.err_list:
            print(err)


if __name__ == '__main__':
    entry_register = EntryRegisterJav()
    entry_register.register_page()

