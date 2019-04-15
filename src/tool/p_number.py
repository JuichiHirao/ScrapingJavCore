import re
import traceback
from .. import db
from .. import data
from .. import site


class ProductNumber:

    def __init__(self, is_log_print: bool = True):
        self.makers = []

        self.is_log_print = is_log_print
        self.log_list = []

        self.maker_dao = db.maker.MakerDao()
        self.jav_dao = db.jav.JavDao()
        self.makers = self.maker_dao.get_all()
        self.fc2 = site.fc2.Fc2()

        self.filter_makers = list(filter(lambda maker:
                                         len(maker.matchProductNumber.strip()) > 0
                                         and len(maker.matchStr) > 0, self.makers))

    def append_maker(self, maker_data: data.MakerData() = None):

        self.makers.append(maker_data)

    def __log_print(self, msg: str = ''):

        if self.is_log_print:
            print(msg)
        else:
            self.log_list.append(msg)

    def get_log_print(self):

        log_list = self.log_list.copy()
        self.log_list.clear()

        return log_list

    def get_registered_p_number(self, jav: data.JavData() = None, match_maker: data.MakerData() = None):

        # jav = data.JavData()
        if jav is None:
            return ''

        if match_maker is None:
            match_maker = data.MakerData()

        if match_maker.name == 'SITE':
            return jav.productNumber.lower()

        if match_maker.kind == 3:
            return jav.productNumber.lower()

        return jav.productNumber.upper()

    def get_p_number(self, title: str = ''):

        return self.__get_p_number(title)

    def __get_p_number(self, title: str = ''):

        match = re.search('[0-9A-Za-z]*-[0-9A-Za-z]*', title)

        if match:
            return match.group().upper()

        return ''

    def get_p_number_hey(self, title: str = ''):

        if len(title) <= 0:
            return 0

        p_number = ''
        label = ''
        m1 = re.search('4[0-9]{3}-PPV[0-9]{3,4}', title)
        m2 = re.search('4[0-9]{3}-[0-9]{3,4}', title)
        if m1 or m2:
            if m1:
                p_number = m1.group().replace('-', '_').replace('PPV', '')
            else:
                p_number = m2.group().replace('-', '_')

        if len(p_number) > 0:
            label = re.sub(p_number + '.*', '', title)

        return p_number, label

    def get_maker_match_number(self, match_maker: data.MakerData(), title: str = ''):

        if match_maker is None:
            return self.__get_p_number(title)

        if len(match_maker.matchProductNumber.strip()) > 0:
            m = re.search(match_maker.matchProductNumber, title, flags=re.IGNORECASE)
            p_number = m.group().strip()

        else:
            match = re.search(match_maker.matchStr + '[-]*[A-Za-z0-9]{2,5}', title, flags=re.IGNORECASE)

            if match:
                p_number = match.group().upper()
            else:
                raise Exception('matchStr[' + match_maker.matchStr + '] するp_numberがないよー [' + title + ']')

        return p_number

    # Javに、メーカー名、レーベルが存在する場合
    # OK
    #    1 : メーカー名と一致（レーベル未チェック）
    #    2 : メーカー名と複数一致で、matchStrと1件だけ一致（レーベル未チェック）
    #    3 : メーカー名と複数一致で、matchStr・レーベル名と1件だけ一致
    # NG
    #   -1 : メーカー名に一致するmaker無し
    #   -2 : メーカー名1件だけ完全一致したが、match_strの文字列がtitleにない
    #   -3 : メーカー一致が複数件、match_strに一致するmaker無し
    #   -4 : メーカー一致が複数件、match_strに複数件、レーベルに一致するmaker無し
    #   -5 : メーカー・レーベルのどちらにも複数一致
    #   -6 : -2の中、メーカー名1件だけ完全一致したが、match_strの文字列がtitleにない（Exception発生）
    def __get_maker_exist_name(self, maker_name: str = '', label_name: str = '', title: str = ''):

        result_maker = None
        ng_reason = 0

        if len(maker_name.strip()) <= 0:
            return '', result_maker, 0

        # jav.makerで検索
        find_filter_maker = filter(lambda maker: len(maker.matchName) > 0 and re.match(maker.matchName, maker_name),
                                   self.makers)
        find_list_maker = list(find_filter_maker)

        if len(find_list_maker) <= 0:
            self.__log_print('javのメーカ名：ラベル名【' + maker_name + ':' + label_name + '】'
                             'に一致するメーカーは存在しません ' + title)
            ng_reason = -1
            return '', result_maker, ng_reason

        if len(find_list_maker) == 1:
            match_maker = find_list_maker[0]
            # 1つだけの場合は、match_strに文字列が存在するかのチェック
            if re.search(match_maker.matchStr, title, re.IGNORECASE) or re.search(
                    match_maker.matchProductNumber, title, re.IGNORECASE):
                ng_reason = 1
                result_maker = match_maker
                self.__log_print('OK メーカー完全一致と、タイトル内に製品番号一致 [' + maker_name + ']' + title)
                try:
                    p_number = self.get_maker_match_number(match_maker, title)
                except Exception as err:
                    print('Exception jav maker [' + maker_name + '] label [' + label_name + '] title [' + title + ']' + str(err))
                    ng_reason = -6
                    self.__log_print('NG メーカー完全一致だが、タイトル内に製品番号が一致しない [' + maker_name + ']' + title)
                    p_number = self.__get_p_number(title)

            else:
                ng_reason = -2
                self.__log_print('NG メーカー完全一致だが、タイトル内に製品番号が一致しない [' + maker_name + ']' + title)
                p_number = self.__get_p_number(title)

            return p_number, result_maker, ng_reason

        # jav.makerが複数件一致した場合はさらに掘り下げる

        # レーベル名より、match_strが一致しているのをまずはチェック
        find_filter_label = filter(lambda maker: re.search(maker.matchStr + '[\-0-9]', title, re.IGNORECASE),
                                   find_list_maker)
        find_list_label = list(find_filter_label)
        if len(find_list_label) <= 0:
            self.__log_print('NG メーカー一致が複数件、match_strに一致するmaker無し [' + maker_name + ':' + label_name + ']' + title)
            ng_reason = -3
            p_number = self.__get_p_number(title)

            return p_number, result_maker, ng_reason

        if len(find_list_label) == 1:
            result_maker = find_list_label[0]
            ng_reason = 2
            self.__log_print('OK メーカーと、タイトル内に製品番号一つだけ一致 [' + maker_name + ':' + label_name + ']' + title)
            p_number = self.get_maker_match_number(result_maker, title)

            return p_number, result_maker, ng_reason

        # match_strのチェックが終了して、複数件の場合、レーベル名をチェック
        else:
            try:
                if len(label_name) <= 0:
                    find_filter_label = filter(lambda maker: len(maker.label) == 0, find_list_label)
                else:
                    find_filter_label = filter(lambda maker: re.search(maker.matchLabel, label_name, re.IGNORECASE)
                                               and len(maker.matchLabel) > 0, find_list_label)
                find_list_label = list(find_filter_label)
            except TypeError as terr:
                print('TypeError 発生')
                print('label_name [' + label_name + ']')
                print('matchLabel')
                print(str(find_list_label))
                raise terr

        if len(find_list_label) <= 0:
            ng_reason = -4
            self.__log_print('NG メーカー一致が複数件、match_strに複数件、レーベル名に一致するmaker無し ['
                             + maker_name + ':' + label_name + ']' + title)
            p_number = self.get_maker_match_number(result_maker, title)

            return p_number, result_maker, ng_reason

        if len(find_list_label) == 1:
            result_maker = find_list_label[0]
            ng_reason = 3
            self.__log_print('OK メーカーと、タイトル内に製品番号複数一致 & label一致 [' + maker_name + ':' + label_name + ']' + title)
            p_number = self.get_maker_match_number(result_maker, title)

            return p_number, result_maker, ng_reason

        # labelにも複数一致した場合
        ng_reason = -5
        self.__log_print('NG メーカー・レーベルのどちらにも複数一致 name [' + maker_name + '] label [' + label_name + ']' + title)
        p_number = self.__get_p_number(title)

        return p_number, result_maker, ng_reason

    # Javに、メーカー名、レーベルが存在しない場合
    # OK
    #    11 : match_strとmatchProductNumberに1件だけ一致
    #    12 : SITEのmatchStrとサイト名が一致、matchProductNumberでp_numberを取得
    # NG
    #   -11 : match_strとmatchProductNumberに複数件が一致
    #   -12 : SITEに一致したが、p_numberの取得が出来ない
    def __get_maker_not_exist_name(self, title: str = ''):

        ng_reason = 0
        result_maker = None
        find_list_maker = []
        for maker in self.makers:
            if maker.name == 'SITE' and re.search(maker.matchStr, title, flags=re.IGNORECASE):
                match = re.search(maker.matchProductNumber, title, flags=re.IGNORECASE)
                # ' [a-z0-9_]* ', title, flags=re.IGNORECASE)

                if match:
                    ng_reason = 12
                    p_number = match.group()
                    self.__log_print('INFO SITE MATCH p_number [' + p_number.strip() + ']   ' + title + ']')
                    return p_number.strip(), maker, ng_reason
                else:
                    ng_reason = -12
                    self.__log_print('NG SITEに一致したが、p_numberの取得が出来ない ' + title + ']')
                    return '', result_maker, ng_reason

        for maker in self.filter_makers:
            if re.search(maker.matchStr, title, flags=re.IGNORECASE) \
                    and re.search(maker.matchProductNumber, title, flags=re.IGNORECASE):
                find_list_maker.append(maker)

        if len(find_list_maker) <= 0:
            self.__log_print('INFO タイトルからmatchProductNumberに一致するメーカー無し [' + title + ']')

            return '', result_maker, ng_reason

        if len(find_list_maker) == 1:
            result_maker = find_list_maker[0]
            ng_reason = 11
            self.__log_print(
                'OK matchProductNumberに1件だけ一致 '
                '[' + result_maker.matchStr + '] [' + result_maker.matchProductNumber + '] ' + title)
            p_number = self.get_maker_match_number(result_maker, title)

            return p_number, result_maker, ng_reason

        self.__log_print('NG タイトルからmatchProductNumberに複数一致 [' + title + ']')
        ng_reason = -11
        p_number = self.get_maker_match_number(find_list_maker[0], title)

        return p_number, result_maker, ng_reason

    # こいつは最後の砦なので、ng_reasonに0はリターンしない
    # Javに情報がないので、productNumberをタイトル内から取得して、チェック
    # OK
    #    21 : タイトル内にpNumberと1件だけ一致
    # NG
    #   -21 : タイトル内にpNumberは存在したが、一致するメーカーは存在しない
    #   -22 : タイトル内にpNumberは存在、複数件のメーカーが一致
    #   -23 : タイトル内にpNumberらしき文字列【[0-9A-Za-z]*-[0-9A-Za-z]】*が存在しない
    def __get_match_maker_force(self, title: str = ''):

        p_number = self.__get_p_number(title)
        result_maker = None

        if len(p_number) > 0:
            p_maker = p_number.split('-')[0]

            find_filter_maker = filter(lambda maker: maker.matchStr.upper() == p_maker.upper(), self.makers)
            find_list_maker = list(find_filter_maker)

            if len(find_list_maker) <= 0:
                ng_reason = -21
                self.__log_print('NG タイトル内の製品番号[' + p_number + ']に一致するメーカー無し ' + title)

                return p_number, result_maker, ng_reason

            if len(find_list_maker) == 1:
                result_maker = find_list_maker[0]
                ng_reason = 21
                self.__log_print('OK タイトル内の製品番号[' + p_number + ']に1件だけメーカー一致 ' + title)

                return p_number, result_maker, ng_reason

            ng_reason = -22
            self.__log_print('NG タイトル内の製品番号[' + p_number + ']に複数一致 ' + title)

        else:
            ng_reason = -23
            self.__log_print('NG タイトル内に製品番号【[0-9A-Za-z]*-[0-9A-Za-z]*】の文字列が存在しない [' + title)

        return p_number, result_maker, ng_reason

    def parse(self, jav: data.JavData, is_check):

        # NG
        #   -1 : メーカー名に一致するmaker無し
        #   -2 : メーカー名1件だけ完全一致したが、match_strの文字列がtitleにない
        #   -3 : メーカー一致が複数件、match_strに一致するmaker無し
        #   -4 : メーカー一致が複数件、match_strに複数件、レーベルに一致するmaker無し
        #   -5 : メーカー・レーベルのどちらにも複数一致
        #   -6 : -2の中、メーカー名1件だけ完全一致したが、match_strの文字列がtitleにない（Exception発生）
        edit_label = jav.label.replace('—-', '')
        p_number, match_maker, ng_reason = self.__get_maker_exist_name(jav.maker, edit_label, jav.title)

        # NG
        #   -11 : match_strとmatchProductNumberに複数件が一致
        if ng_reason == 0:
            p_number, match_maker, ng_reason = self.__get_maker_not_exist_name(jav.title)

        # NG
        #   -21 : タイトル内にpNumberは存在したが、一致するメーカーは存在しない
        #   -22 : タイトル内にpNumberは存在、複数件のメーカーが一致
        #   -23 : タイトル内にpNumberらしき文字列【[0-9A-Za-z]*-[0-9A-Za-z]】*が存在しない
        if ng_reason == 0:
            p_number, match_maker, ng_reason = self.__get_match_maker_force(jav.title + ' ' + jav.package)

        return p_number, match_maker, ng_reason

    def parse_and_fc2(self, jav: data.JavData, is_check):

        p_number = ''
        sell_date = ''
        seller = ''
        is_nomatch = False
        match_maker = None
        # match = re.search('[0-9A-Za-z]*-[0-9A-Za-z]*', jav.title)
        if jav.id == 2076:
            i = 0

        # jav.makerが存在する場合（ほぼAVRIP）
        ng_reason = 0
        if len(jav.maker.strip()) > 0:
            if jav.maker == jav.label:
                jav.label = ''
            # 「妄想族」のためにスラッシュは置換
            maker_name = jav.maker.replace('/', '／')

            # jav.makerで検索
            # find_filter_maker = filter(lambda maker: maker.name == maker_name, self.makers)
            find_filter_maker = filter(lambda maker: len(maker.matchName) > 0 and re.match(maker.matchName, maker_name),
                                       self.makers)
            find_list_maker = list(find_filter_maker)

            # jav.makerで1件だけ一致
            if len(find_list_maker) == 1:
                match_maker = find_list_maker[0]
                if re.search(match_maker.matchStr, jav.title, re.IGNORECASE) or re.search(
                        match_maker.matchProductNumber, jav.title, re.IGNORECASE):
                    self.__log_print('OK メーカー完全一致と、タイトル内に製品番号一致 [' + jav.maker + ']' + jav.title)
                    if not is_check:
                        ng_reason = 1
                        self.jav_dao.update_checked_ok(ng_reason, match_maker.id, jav)
                else:
                    self.__log_print('NG メーカー完全一致だが、タイトル内に製品番号が一致しない [' + jav.maker + ']' + jav.title)
                    ng_reason = -1
                    is_nomatch = True

            # jav.makerが複数件一致した場合はさらに掘り下げる
            elif len(find_list_maker) > 1:
                find_filter_label = filter(lambda maker: re.search(maker.matchStr, jav.title, re.IGNORECASE),
                                           find_list_maker)
                find_list_label = list(find_filter_label)
                len_label = len(find_list_label)
                if len_label == 1:
                    match_maker = find_list_label[0]
                    self.__log_print('OK メーカーと、タイトル内に製品番号一つだけ一致 [' + jav.maker + ':' + jav.label + ']' + jav.title)
                    if not is_check:
                        ng_reason = 2
                        self.jav_dao.update_checked_ok(ng_reason, match_maker.id, jav)
                elif len_label > 1:
                    if len(jav.label) <= 0:
                        find_filter_label = filter(lambda maker: len(maker.label) == 0, find_list_label)
                    else:
                        find_filter_label = filter(lambda maker: maker.label == jav.label, find_list_label)
                    find_list_label = list(find_filter_label)
                    if len(find_list_label) == 1:
                        match_maker = find_list_label[0]
                        self.__log_print('OK メーカーと、タイトル内に製品番号複数一致 & label一致 [' + jav.maker + ':' + jav.label + ']' + jav.title)
                        if not is_check:
                            ng_reason = 3
                            self.jav_dao.update_checked_ok(ng_reason, match_maker.id, jav)
                    else:
                        self.__log_print('NG メーカーと、タイトル内に製品番号複数一致 [' + jav.maker + ']' + jav.title)
                        ng_reason = -2
                else:
                    # juyなど、Madonnaとマドンナで英語日本語でマッチしない場合はここにくる
                    self.__log_print('NG ' + str(len(find_list_maker)) + ' メーカーには複数一致、製品番号に一致しない ID [' + str(
                        jav.id) + '] jav [' + jav.maker + ':' + jav.label + ']' + '  maker [' + find_list_maker[
                              0].name + ']' + jav.title)
                    ng_reason = -3
                    is_nomatch = True
                # self.__log_print(str(len(find_list_maker)) + ' ' + jav.maker)
            else:
                self.__log_print('maker exist no match, not register [' + jav.maker + ':' + jav.label + '] ' + jav.title)
                ng_reason = -4
                is_nomatch = True

            if match_maker:
                match = re.search(match_maker.matchStr + '[-]*[A-Za-z0-9]{2,5}', jav.title, flags=re.IGNORECASE)

                if match:
                    p_number = match.group().upper()
                else:
                    is_nomatch = True
                    self.__log_print('メーカー[' + str(
                        match_maker.id) + '] に一致したが、タイトル内に[' + match_maker.matchStr + '] の文字列がない ' + jav.title)
                    ng_reason = -5

        # javのメーカ名が無い場合
        else:
            '''
            find_filter_maker = filter(
                lambda maker: re.search(maker.matchStr, jav.title, flags=re.IGNORECASE)
                              and re.search(maker.matchProductNumber, jav.title,
                                            flags=re.IGNORECASE), self.filter_makers)
            '''
            # find_filter_maker = []
            find_list_maker = []
            for maker in self.filter_makers:
                if re.search(maker.matchStr, jav.title, flags=re.IGNORECASE) \
                        and re.search(maker.matchProductNumber, jav.title, flags=re.IGNORECASE):
                    find_list_maker.append(maker)

            # find_list_maker = list(find_filter_maker)
            match_maker = None
            p_number = ''
            if len(find_list_maker) == 1:
                match_maker = find_list_maker[0]
                m = re.search(match_maker.matchProductNumber, jav.title, flags=re.IGNORECASE)
                p_number = m.group().strip()
                if not match_maker.label:
                    match_maker.label = ''
                self.__log_print(
                    'OK jav.maker無し 製品番号に1件だけ一致 [' + p_number + ']' + match_maker.name + ':' + match_maker.label + ' ' + jav.title)

                if match_maker.pNumberGen == 1:
                    m = re.search(match_maker.matchProductNumber, jav.title, flags=re.IGNORECASE)
                    m_m = re.search('\([0-9]{4}', match_maker.matchStr)
                    if m_m:
                        m_number = m_m.group()
                    else:
                        self.__log_print("HEY動画のmakerのmatchStrの列が(4083|本生素人TV)の形式になっていません")
                        exit(-1)
                    p_number = m_number.replace('(', '') + '_' + m.group().replace('PPV', '')
                else:
                    p_number = m.group().strip()
                if not is_check:
                    ng_reason = 4
                    self.jav_dao.update_checked_ok(ng_reason, match_maker.id, jav)
            elif len(find_list_maker) > 1:
                self.__log_print(str(len(find_list_maker)) + ' many match ' + jav.title)
                ng_reason = -6
            elif len(find_list_maker) <= 0:
                # self.__log_print(str(len(find_list_maker)) + ' no match ' + jav.title)
                is_nomatch = True
                ng_reason = -7

            if jav.isSite == 0:
                if match_maker is not None:
                    if match_maker.siteKind == 1:
                        seller, sell_date = self.fc2.get_info(p_number)
                        # self.__log_print('    ' + seller + ' ' + sell_date)

        # HEY動画でAV9898など配信名しか入っていない場合の処理
        '''
        if ng_reason == -7:
            title_plus_file = jav.title + ' ' + jav.package
            find_filter_label = filter(lambda maker: re.search(maker.matchName, title_plus_file, re.IGNORECASE),
                                       self.makers)
            find_list_label = list(find_filter_label)
            if len(find_list_label) > 0:
                self.__log_print(jav.title)
        '''

        if ng_reason < 0:
            if not is_check:
                self.jav_dao.update_checked_ok(ng_reason, 0, jav)

        if is_nomatch:
            p_number = ''
            match = re.search('[0-9A-Za-z]*-[0-9A-Za-z]*', jav.title)

            if match:
                p_number = match.group().strip()
                p_maker = p_number.split('-')[0]
                find_filter_maker = filter(lambda maker: maker.matchStr.upper() == p_maker.upper(), self.makers)
                find_list_maker = list(find_filter_maker)
                if len(find_list_maker) == 1:
                    match_maker = find_list_maker[0]
                    self.__log_print(
                        'OK 製品番号PARSE maker.matchStrに1件だけ一致 [' + p_number + ']  match_str [' + p_maker + ']' + match_maker.name + ':' + match_maker.label)
                    ng_reason = 5
                    if not is_check:
                        self.jav_dao.update_checked_ok(ng_reason, match_maker.id, jav)
                if len(find_list_maker) > 1:
                    self.__log_print('NG 製品番号PARSE maker.matchStrに複数一致 [' + str(jav.id) + '] ' + jav.title)
                if len(find_list_maker) <= 0:
                    self.__log_print('NG [' + str(
                        jav.id) + '] is_nomatch メーカー[' + jav.maker + ':' + jav.label + ']  は、movie_makersに存在しない  ' + jav.title)

        return p_number, seller, sell_date, match_maker, ng_reason
