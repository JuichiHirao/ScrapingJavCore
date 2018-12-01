import re
import os
import sys
from .. import data
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class ImagePathNotFoundError(Exception):
    pass


class DriverNotFoundError(Exception):
    pass


class Environment:

    def __init__(self):

        self.options = Options()
        self.options.add_argument('--headless')

        self.driver = None
        self.imagePath = ''

        if os.name == 'nt':
            self.__set_windows()
        elif os.name == 'posix' and 'linux' in sys.platform:
            print('linux')
            self.__set_linux()
        elif os.name == 'posix':
            print('macos')
            self.__set_macos()
        else:
            print('other os.name' + os.name + '] sys.platform [' + sys.platform + ']')

    def get_driver(self):
        return self.driver

    def get_image_path(self):
        return self.imagePath

    def __set_windows(self):

        driver_path = 'c:\\SHARE\\chromedriver.exe'

        if not os.path.isfile(driver_path):
            raise DriverNotFoundError(driver_path + 'に存在しません')

        self.driver = webdriver.Chrome(chrome_options=self.options,
                                       executable_path='c:\\SHARE\\chromedriver.exe')

        self.imagePath = "D:\DATA\jav-save"

        if not os.path.isdir(self.imagePath):
            raise ImagePathNotFoundError(self.imagePath + 'に存在しません')

    def __set_macos(self):

        self.driver = webdriver.Chrome(chrome_options=self.options)

        self.imagePath = "/Users/juichihirao/jav-jpeg"
        if not os.path.exists(self.imagePath):
            raise ImagePathNotFoundError(self.imagePath + 'に存在しません')

    def __set_linux(self):

        self.driver = webdriver.Chrome(chrome_options=self.options)

        self.imagePath = "~root/jav-jpeg"
        if not os.path.exists(self.imagePath):
            raise ImagePathNotFoundError(self.imagePath + 'に存在しません')


class CopyText:

    def __init__(self, is_debug: bool = False):
        self.is_debug = is_debug

    def get_title(self, copy_text: str = '', product_number: str = '', match_maker: data.MakerData = None):

        hankaku_kigou = ['/', ':']
        zenkaku_kigou = ['／', '：']
        hankaku = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', ' ']
        zenkaku = ['１', '２', '３', '４', '５', '６', '７', '８', '９', '０', '　']
        movie_kind = ''

        if match_maker:
            if match_maker.replaceWords is not None and len(match_maker.replaceWords) > 0:
                words = match_maker.replaceWords.split(' ')
                for word in words:
                    copy_text = re.sub(word, '', copy_text)

        # re_movie = re.compile(self.movie_extension, re.IGNORECASE)

        match_search = re.search('[\[]*FHD[\]]*', copy_text)
        if match_search:
            movie_kind = ' FHD'
            copy_text = copy_text.replace(match_search.group(), '')

        re_replace = re.compile(product_number, re.IGNORECASE)
        title = re.sub(re_replace, '', copy_text.strip())

        if len(movie_kind) > 0:
            title = title.strip() + movie_kind

        if match_maker:
            match_maker_name = re.search(match_maker.matchName, title)
            if match_maker_name:
                title = title.replace(match_maker_name.group(), '')

            match_maker_str = re.search(match_maker.matchStr, title)
            if match_maker_str:
                title = title.replace(match_maker_str.group(), '')

        edit_copytext = title
        for idx, char in enumerate(zenkaku):
            m = re.search(char, edit_copytext)
            if m:
                edit_copytext = edit_copytext.replace(char, hankaku[idx])

        for idx, char in enumerate(hankaku_kigou):
            m = re.search(char, edit_copytext)
            if m:
                edit_copytext = edit_copytext.replace(char, zenkaku_kigou[idx])

        title = edit_copytext

        if self.is_debug:
            print('  before [' + copy_text + ']')
            print('  after  [' + title.strip() + ']')

        return title.strip()
