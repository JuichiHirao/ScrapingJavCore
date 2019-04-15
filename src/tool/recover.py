import re
import traceback
from .. import common
from .. import db
from .. import data
from .. import site
from .. import tool


class RecoverError(Exception):
    pass


class Recover:

    def __init__(self, site_collect: site.SiteInfoCollect = None, is_log_print: bool = True, is_dry_run: bool = True,
                 makers: list = None):
        self.p_tool = tool.p_number.ProductNumber(is_log_print=False)
        self.makers = []

        self.is_log_print = is_log_print
        self.log_list = []
        self.is_dry_run = is_dry_run

        self.maker_dao = db.maker.MakerDao()
        self.jav_dao = db.jav.JavDao()

        if makers is None:
            self.makers = self.maker_dao.get_all()
        else:
            self.makers = makers

        self.parser = common.AutoMakerParser()
        if site_collect is None:
            self.site_collect = site.SiteInfoCollect()
            self.site_collect.initialize()
        else:
            self.site_collect = site_collect

        self.filter_makers = list(filter(lambda maker:
                                         len(maker.matchProductNumber.strip()) > 0
                                         and len(maker.matchStr) > 0, self.makers))

        self.err_list = []

    def get_error_detail(self):

        return self.err_list

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

    def is_not_dry_run(self):

        if self.is_dry_run is None or self.is_dry_run:
            return False

        return True

    def get_ng_new_maker(self, p_number: str = '', ng_reason: int = 0, jav: data.JavData() = None):
        """
        新規登録するメーカーのチェック

        :param p_number:
        :param ng_reason:
        :param jav:
        :return:
        """

        new_maker = None
        site_data = None

        if 'AVOP-' in jav.productNumber.upper():
            try:
                new_maker = self.parser.get_maker_no_check(jav)
                # self.p_tool.append_maker(new_maker)
            except common.MatchStrSameError as err:
                self.err_list.append('MatchStrがscraping.makerに既に存在' + str(err))
                raise RecoverError('[' + str(jav.id) + '] -1から-3でMatchStrSameError発生 ' + jav.title)

            return new_maker, site_data

        # -1 : メーカー名に一致するmaker無し
        # -3 : メーカー一致が複数件、match_strに一致するmaker無し
        #   メーカーに登録
        # -2 : メーカー名1件だけ完全一致したが、match_strの文字列がtitleにない
        #   match_strに完全一致のメーカーをdelete:1にして、新規としてメーカーに登録
        if ng_reason == -1 or ng_reason == -2 or ng_reason == -3:
            if ng_reason == -2:
                self.err_list.append('-2発生、1件一致の[' + jav.productNumber + ']deletedを1にする必要あり')

                # deleted : 1 に更新
                # arr_match_str = jav.productNumber.split('-')
                # makers = self.maker_dao.get_where_agreement('WHERE match_str = %s', (arr_match_str[0]))
                # if makers is not None and len(makers) == 1:
                #     if self.is_not_dry_run():
                #         self.maker_dao.update_deleted(1, makers[0])
                # else:
                #     self.err_list.append('-2発生、1件一致のmaker [' + jav.productNumber + '] 発見できず')
            try:
                new_maker = self.parser.get_maker(jav)
                # self.p_tool.append_maker(new_maker)
            except common.MatchStrSameError as err:
                self.err_list.append('MatchStrがscraping.makerに既に存在' + str(err))
                raise RecoverError('[' + str(jav.id) + '] -1から-3でMatchStrSameError発生 ' + jav.title)

        #   -21 : タイトル内にpNumberは存在したが、一致するメーカーは存在しない
        if ng_reason == -21:
            hey_p_number, hey_label = self.p_tool.get_p_number_hey(jav.title)

            if len(hey_p_number) > 0:

                self.err_list.append('      [' + hey_p_number + '] 【' + hey_label + '】')
                site_data = self.site_collect.hey.get_info(hey_p_number)
                if site_data is None or len(site_data.maker) <= 0:
                    self.err_list.append('      HEYのp_number[ ' + hey_p_number + ']だが、HEYのサイトには存在しない ' + jav.title)
                    raise RecoverError('-21でHEYのサイトで詳細が存在しないため発生')

                makers = self.maker_dao.get_where_agreement('WHERE label = %s', (site_data.maker, ))

                if makers is not None:
                    self.err_list.append('      [' + site_data.streamDate + '] 【' + site_data.maker + '】')
                    self.err_list.append('      HEY【' + site_data.maker + '】はmakerに存在 maker_id ['
                                         + str(makers[0].id) + ']')
                    raise RecoverError('-21でHEYでmakerに同様の提供元が存在で発生')

                self.err_list.append('      [' + site_data.streamDate + '] 【' + site_data.maker + '】')
                new_maker = self.parser.get_maker_hey(hey_p_number, site_data)

            else:
                site_data = self.site_collect.mgs.get_info(jav.productNumber)

                site_name = 'MGS'
                if site_data is None or len(site_data.productNumber) <= 0:
                    self.err_list.append('      MGSには存在しない ' + jav.title)
                    site_data = self.site_collect.fanza.get_info(p_number)
                    if site_data is None:
                        self.err_list.append('    FANZAにも存在しない')
                        raise RecoverError('-21でFANZAのサイトには未存在で発生')

                    site_name = 'FANZA'
                    site_data.productNumber = jav.productNumber
                try:
                    new_maker = self.parser.get_maker_from_site(site_data, site_name)
                except common.MatchStrNotFoundError as err:
                    self.err_list.append('MatchStrがタイトル内に存在しない' + str(err) + jav.title)
                    raise RecoverError('[' + str(jav.id) + '] -21でMatchStrNotFoundError発生 ' + jav.title)

        # maker、labelを更新
        # -22 : タイトル内にpNumberは存在、複数件のメーカーが一致
        if ng_reason == -22:
            site_data = self.site_collect.fanza.get_info(p_number)
            if site_data is None:
                self.err_list.append('    FANZAには存在しない')
            else:
                self.err_list.append('    FANZA 【' + site_data.streamDate + '】')
                # if self.is_not_dry_run():
                #     if len(jav.maker) <= 0:
                #         self.jav_dao.update_maker_label(site_data.maker, site_data.label, jav.id)

        # productNumberを更新
        # -21 : タイトル内にpNumberは存在したが、一致するメーカーは存在しない
        # -22 : タイトル内にpNumberは存在、複数件のメーカーが一致
        # -23 : タイトル内にpNumberらしき文字列【[0-9A-Za-z]*-[0-9A-Za-z]】*が存在しない
        # if ng_reason == -21 or ng_reason == -22 or ng_reason == -23:
        #     if p_number != jav.productNumber:
        #         self.err_list.append('  p_number change [' + p_number + '] <-- [' + jav.productNumber + ']')
        #        # if self.is_not_dry_run():
        #        #     self.jav_dao.update_product_number(jav.id, p_number)

        if new_maker is not None:
            if len(list(filter(lambda maker: maker.matchStr.upper() == new_maker.matchStr.upper(), self.makers))) > 0:
                self.err_list.append('new_makerのmatch_str[' + new_maker.matchStr + ']は既にscraping.makerに存在')
                raise RecoverError('new_makerのmatch_strは既にscraping.makerに存在')
        '''
        if new_maker is not None:
            new_maker.print('NEW ')
            if self.is_not_dry_run():
                self.maker_dao.export(new_maker)
        '''
        return new_maker, site_data

