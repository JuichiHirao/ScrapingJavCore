import re
import os
import sys
from datetime import datetime
from .. import data
from .. import db
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

        if match_maker:
            if match_maker.replaceWords is not None and len(match_maker.replaceWords) > 0:
                words = match_maker.replaceWords.split('¥t')
                for word in words:
                    if '/' in word:
                        # print('/【' + word[1:-1] + '】')
                        replace_before_after = word[1:-1].split('/')
                        # print('/0【' + replace_before_after[0] + '】')
                        # print('/1【' + replace_before_after[1] + '】')
                        m = re.search(replace_before_after[0], edit_copytext)
                        replace_after = replace_before_after[1]
                        if m:
                            m_rename = re.search(re.escape('(?P<') + '[a-zA-Z]*' + re.escape('>')
                                                 , replace_before_after[0])
                            # m_rename = re.search(re.escape('(?P<age>'), replace_before_after[0])
                            if m_rename:
                                re_name = m_rename.group()[4:-1]
                                replace_after = replace_before_after[1].replace(re_name, m.group(re_name))
                                if self.is_debug:
                                    print('re_name [' + re_name + ']' + m.group(re_name)
                                          + '  replace_after 【' + replace_after + '】')
                            else:
                                if self.is_debug:
                                    print('no match ' + m.group('age'))
                        edit_copytext = re.sub(replace_before_after[0], replace_after, edit_copytext)
                    else:
                        if self.is_debug:
                            print(' ' + word)
                        edit_copytext = re.sub(word, '', edit_copytext)
                    # print(word + ' [' + copy_text + ']')

        title = edit_copytext

        if self.is_debug:
            print('  before [' + copy_text + ']')
            print('  after  [' + title.strip() + ']')

        return title.strip()


class ImportParser:

    def __init__(self):
        self.replace_info_dao = db.replace_info.ReplaceInfoDao()
        self.replace_info_list = self.replace_info_dao.get_all()

    def get_actress(self, jav: data.JavData() = None):

        actress = ''
        for replace_info in self.replace_info_list:
            if replace_info.sourceType == 'text':
                if len(actress) <= 0:
                    actress = jav.actress.replace(replace_info.source, replace_info.destination)
                else:
                    actress = actress.replace(replace_info.source, replace_info.destination)

        if ' ' in actress:
            actress_list = actress.split(' ')
            actress = ','.join(actress_list)

        return actress

    def get_filename(self, import_data: data.ImportData() = None):

        if import_data is None:
            return ''

        # import_data = data.ImportData()
        kind_str = ''
        if import_data.kind == 1:
            kind_str = '[AVRIP]'
        elif import_data.kind == 2:
            kind_str = '[IVRIP]'
        elif import_data.kind == 3:
            kind_str = '[裏AVRIP]'
        elif import_data.kind == 4:
            kind_str = '[DMMR-AVRIP]'
        elif import_data.kind == 5:
            kind_str = '[DMMR-IVRIP]'

        try:
            sell_date_str = import_data.sellDate.strftime('%Y%m%d')
        except AttributeError:
            return ''

        filename = kind_str + '【' + import_data.maker.strip() + '】' + import_data.title + ' ' \
                   + '[' + import_data.productNumber + ' ' + sell_date_str + ']'

        return filename


class MatchStrNotFoundError(Exception):
    pass


class MatchStrSameError(Exception):
    pass


class AutoMakerParser:

    def __init__(self, maker_dao: db.maker.MakerDao = None):
        self.replace_info_dao = db.replace_info.ReplaceInfoDao()
        self.replace_info_list = self.replace_info_dao.get_where_agreement('WHERE type like \'maker%\'')

        if not maker_dao:
            self.maker_dao = db.maker.MakerDao()
        else:
            self.maker_dao = maker_dao

        # INSERT INTO replace_info (type, source, destination) VALUES('maker_name', 'プレステージ', 'PreStige');
        # INSERT INTO replace_info (type, source, destination) VALUES('maker_m_name', 'プレステージ', 'プレステージ');

    def get_maker(self, jav: data.JavData()):

        m_p = re.search('[A-Z0-9]{2,5}-[A-Z0-9]{2,4}', jav.title, re.IGNORECASE)

        if m_p:
            p_number = m_p.group()
            match_str = p_number.split('-')[0]
        else:
            err_msg = '[' + str(jav.id) \
                      + '] 対象のmatch_strが存在しません [A-Z0-9]{3,5}-[A-Z0-9]{3,4}の正規表現と一致しません' \
                      + jav.title
            raise MatchStrNotFoundError(err_msg)

        if len(match_str) > 0:
            exist_maker = self.maker_dao.get_exist(match_str.upper())
            if exist_maker:
                err_msg = '[' + str(jav.id) + '] 発見!! [' + match_str + ']'
                exist_maker.print()
                raise MatchStrSameError(err_msg)

        maker = data.MakerData()
        maker.name = jav.maker
        maker.kind = 1
        maker.matchStr = match_str.upper()
        maker.label = jav.label
        maker.registeredBy = 'AUTO ' + datetime.now().strftime('%Y-%m-%d')

        maker.name = self.apply_replace_info(jav.maker, ('maker_name', 'maker_m_name'))
        maker.label = self.apply_replace_info(jav.label, ('maker_label', 'maker_m_label'))

        return maker

    def get_maker_from_site(self, site_data: data.SiteData(), site_name: str = ''):

        m_p = re.search('[A-Z0-9]{4,10}-[A-Z0-9]{2,4}', site_data.productNumber, re.IGNORECASE)

        if m_p:
            p_number = m_p.group()
            match_str = p_number.split('-')[0]
        else:
            err_msg = 'site_data.productNumber[' + str(site_data.productNumber) \
                      + '] が所定の形式ではありません [A-Z0-9]{4,10}-[A-Z0-9]{3,4}の正規表現と一致しません'
            raise MatchStrNotFoundError(err_msg)

        maker = data.MakerData()

        if site_name.lower() == 'mgs':
            if site_data.maker == 'プレステージ':
                maker.name = site_data.maker
                maker.matchName = site_data.maker
                maker.label = site_data.label
            else:
                maker.name = site_name
                maker.matchName = site_name
                maker.label = site_data.maker
            maker.siteKind = 2
        else:
            maker.name = site_name
            maker.matchName = site_name
            maker.label = site_data.maker

        maker.kind = 1
        maker.matchStr = match_str.upper()
        maker.registeredBy = 'AUTO ' + datetime.now().strftime('%Y-%m-%d')

        maker.name = self.apply_replace_info(maker.name, ('maker_name', 'maker_m_name'))
        maker.label = self.apply_replace_info(maker.label, ('maker_label', 'maker_m_label'))

        return maker

    def apply_replace_info(self, target_str: str = '', apply_list: list = None):

        apply_str = ''
        for replace_info in self.replace_info_list:
            if apply_list == 'all':
                apply_str = self.__get_type_replace(target_str, replace_info)
            if replace_info.type in apply_list:
                apply_str = self.__get_type_replace(target_str, replace_info)

        return apply_str

    def __get_type_replace(self, target_str: str = '', replace_info: data.ReplaceInfoData = None):

        if replace_info.sourceType == 'text':
            return target_str.replace(replace_info.source, replace_info.destination)

        return ''
