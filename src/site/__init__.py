from . import fc2
from . import wiki
from . import mgs
from . import hey
from . import fanza
from .. import data
from .. import common


class SiteInfoCollect:

    def __init__(self):
        self.fanza = None
        self.fc2 = None
        self.hey = None
        self.mgs = None
        self.sougou_wiki = None
        self.google_wiki = None
        self.site_wiki = None
        self.copy_text = common.CopyText(False)

    def initialize(self):

        if self.sougou_wiki is None:
            self.sougou_wiki = wiki.SougouWiki()
            self.google_wiki = wiki.Google()
            self.site_wiki = wiki.Site()

        if self.fanza is None:
            self.fanza = fanza.Fanza()

        if self.fc2 is None:
            self.fc2 = fc2.Fc2()

        if self.hey is None:
            self.hey = hey.Hey()

        if self.mgs is None:
            self.mgs = mgs.Mgs()


class SiteInfoGetter:

    def __init__(self, site_collect: SiteInfoCollect = None, is_debug: bool = False):
        self.is_debug = is_debug

        if site_collect is None:
            self.site_collect = SiteInfoCollect()
            self.site_collect.initialize()
        else:
            self.site_collect = site_collect

    def get_info(self, jav: data.JavData = None, match_maker: data.MakerData = None):

        site_data = None

        if match_maker.name == 'SITE':
            return site_data

        if site_data is None and 'HEY動画' in match_maker.name:
            site_data = self.site_collect.hey.get_info(jav.productNumber)

        if site_data is None and 'MGS' in match_maker.name or match_maker.siteKind == 2:
            site_data = self.site_collect.mgs.get_info(jav.productNumber)

        if site_data is None and 'FC2' in match_maker.name:
            site_data = self.site_collect.fc2.get_info(jav.productNumber)

        if site_data is None and match_maker.kind == 1:
            if match_maker.siteKind != 3 and match_maker.siteKind != 4:
                site_data = self.site_collect.fanza.get_info(jav.productNumber)

            if site_data is None:
                title = self.site_collect.copy_text.get_title(jav.title, jav.productNumber, match_maker)
                site_data = self.site_collect.fanza.get_info_from_title(title, jav.productNumber)

        if site_data is None and match_maker.kind == 3:
            stream_date = self.site_collect.copy_text.get_date_ura(jav.title)
            if len(stream_date) > 0:
                site_data = data.SiteData()
                site_data.streamDate = stream_date

        return site_data

    def get_wiki(self, jav: data.JavData = None, match_maker: data.MakerData = None):

        if match_maker.kind != 1:
            return ''

        if match_maker.name == 'SITE':
            site_name, site_url = self.site_collect.site_wiki.get_info(match_maker, jav.productNumber)
            result_search = site_name + ' ' + site_url
        else:
            if match_maker.siteKind == 3:
                result_search = self.site_collect.sougou_wiki.search(jav.productNumber)
            # elif match_maker.siteKind == 0:
            else:
                site_name, site_url = self.site_collect.google_wiki.get_info(jav.productNumber)
                result_search = site_name + ' ' + site_url

                if len(site_name) <= 0:
                    result_search = self.site_collect.sougou_wiki.search(jav.productNumber)

        return result_search
