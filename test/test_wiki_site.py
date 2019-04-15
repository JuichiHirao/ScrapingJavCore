import unittest
from src import data
from src import site


# PYTHONPATH=. python test/test_common.py -v
class TestWikiSiteInfo(unittest.TestCase):

    def setUp(self):
        site_info_list = []

        site_info = data.SiteInfoData()
        site_info.name = 'S-CUTE'
        site_info.matchStr = 'S-Cute'
        site_info.targetNumber = '^[56].*'
        site_info.url = '500-600ONLYURL'
        site_info.nameOrder = 0
        site_info_list.append(site_info)

        site_info = data.SiteInfoData()
        site_info.name = 'S-CUTE'
        site_info.matchStr = 'S-Cute'
        site_info.targetNumber = '.*'
        site_info.nameOrder = 99
        site_info.url = '500-600URL'
        site_info_list.append(site_info)

        site_info = data.SiteInfoData()
        site_info.name = '舞ワイフ'
        site_info.matchStr = 'Mywife'
        site_info.targetNumber = '.*'
        site_info.nameOrder = 99
        site_info.url = '800URL'
        site_info_list.append(site_info)

        self.site_wiki = site.wiki.Site(site_info_list=site_info_list)

    def test_ok_match_one(self):
        p_number = '00800'

        match_maker = data.MakerData()
        match_maker.name = 'SITE'
        match_maker.matchName = 'Mywife'

        site_name, site_url = self.site_wiki.get_info(match_maker, p_number)

        self.assertEqual('舞ワイフ', site_name)
        self.assertEqual('800URL', site_url)

    def test_ok_match_many(self):
        p_number = '513_abc_01'

        match_maker = data.MakerData()
        match_maker.name = 'SITE'
        match_maker.matchStr = 'S-Cute'
        match_maker.label = 'S-Cute'

        site_name, site_url = self.site_wiki.get_info(match_maker, p_number)

        self.assertEqual('S-CUTE', site_name)
        self.assertEqual('500-600ONLYURL', site_url)

    def test_ok_match_many_last(self):
        p_number = '900_def_01'

        match_maker = data.MakerData()
        match_maker.name = 'SITE'
        match_maker.matchStr = 'S-Cute'
        match_maker.label = 'S-Cute'

        site_name, site_url = self.site_wiki.get_info(match_maker, p_number)

        self.assertEqual('S-CUTE', site_name)
        self.assertEqual('500-600URL', site_url)

    def test_ng_no_match(self):
        match_maker = data.MakerData()
        match_maker.name = 'AITE'
        match_maker.matchStr = 'S-Cute'
        match_maker.label = 'S-Cute'

        site_name, site_url = self.site_wiki.get_info(match_maker)

        self.assertEqual('', site_name)


if __name__ == "__main__":
    unittest.main()
