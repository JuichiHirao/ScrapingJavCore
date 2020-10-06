import os
from time import sleep
from datetime import datetime
from src import db
from src import data
from src import tool
from src import common
from bs4 import BeautifulSoup
import urllib
import shutil
import socket
import traceback
import selenium


class EntryRegisterJav:

    def __init__(self):

        self.jav_dao = db.jav.JavDao()
        self.err_list = []
        self.p_number_tool = tool.p_number.ProductNumber()
        self.env = common.Environment(False)
        self.driver = self.env.get_driver()
        self.store_path = 'C:\mydata\jav-save'
        """
        # self.env = common.Environment(True)

        self.main_url = "http://maddawgjav.net/"
        # self.main_url = "http://172.67.70.231/"


        self.slack_api = tool.slack.SlackApi()

        self.opener = urllib.request.build_opener()
        self.opener.addheaders = [('User-Agent',
                                   'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
        """

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
            self.driver.get(link)

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

    def register_page(self):

        html_save_path = 'C:\mydata'
        # html_file = 'C:\mydata\Maddawg JAV.html'
        # html_file = 'Maddawg JAV - page 4.html'
        html_file_list = [
            'Maddawg JAV.html',
            'Maddawg JAV - page 2.html',
            'Maddawg JAV - page 3.html',
            'Maddawg JAV - page 4.html',
            'Maddawg JAV - page 5.html',
            'Maddawg JAV - page 6.html',
            'Maddawg JAV - page 7.html',
            'Maddawg JAV - page 8.html'
            # 'Maddawg JAV - page 9.html'
            # 'Maddawg JAV - page 10.html',
            # 'Maddawg JAV - page 11.html',
            # 'Maddawg JAV - page 12.html',
            # 'Maddawg JAV - page 13.html',
            # 'Maddawg JAV - page 14.html',
            # 'Maddawg JAV - page 15.html',
            # 'Maddawg JAV - page 16.html',
            # 'Maddawg JAV - page 17.html',
            # 'Maddawg JAV - page 18.html',
            # 'Maddawg JAV - page 19.html',
            # 'Maddawg JAV - page 20.html',
            # 'Maddawg JAV - page 21.html'
        ]

        for html_file in html_file_list:
            html_pathname = os.path.join(html_save_path, html_file)
            self.__scraping_execute(html_pathname)

    def __scraping_execute(self, html_pathname):

        print(html_pathname)
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

            if title_exist:
                print('title exist ' + jav.title)
                continue

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

            if match_maker is not None:
                jav.makersId = match_maker.id

            self.jav_dao.export(jav)
            jav.print()

            # package ファイルをローカルからローカルへコピー
            div_entry = entry.find('div', class_='entry')
            img_tag = div_entry.find('img')
            if img_tag is not None:
                package_file = 'C:\mydata\\' + img_tag['src']

                if os.path.exists(package_file):
                    filename = os.path.basename(package_file)
                    print('exist file {} {}'.format(filename, package_file))
                    exist_id = self.jav_dao.get_exist_id(jav.title)
                    if exist_id < 0:
                        print('not exist path')
                    else:
                        dest_pathname = 'C:\mydata\jav-save\\' + filename
                        shutil.copy2(package_file, dest_pathname)
                        self.jav_dao.update_package(exist_id, filename)
                else:
                    print(img_tag['src'])
            else:
                print('not found img')

            # thumbnail ファイルをネットから取得
            a_list = entry.find_all('a')
            for a in a_list:
                if 'https://pixhost' in a['href']:
                    thumbnail_link = a['href']
                    links = []
                    print(thumbnail_link)
                    links.append(thumbnail_link)
                    thumbnail_files = self.__download_thumbnails(links)
                    if len(thumbnail_files) > 0:
                        exist_id = self.jav_dao.get_exist_id(jav.title)
                        if exist_id > 0:
                            self.jav_dao.update_thumbnail(exist_id, thumbnail_files)

        # exit(-1)


if __name__ == '__main__':
    entry_register = EntryRegisterJav()
    entry_register.register_page()
