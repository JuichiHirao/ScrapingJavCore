import unittest
from javcore import common
from javcore import data


class TestCopyText(unittest.TestCase):

    def test_scute(self):
        match_maker = data.MakerData()
        match_maker.matchName = 'SITE'
        match_maker.matchStr = 'S-Cute'
        match_maker.matchProductNumber = '[0-9]{3}_[a-zA-Z]*_[a-zA-Z]*[0-9]{1,2}|htr_[0-9]{3}|[a-zA-Z]*_[0-9]{3}'
        expected = '視線も体もセクシーな美女の誘惑SEX／Nao'
        copy_text = common.CopyText()
        actual = copy_text.get_title('S-Cute 609_nao_k04 視線も体もセクシーな美女の誘惑SEX／Nao'
                                     , '609_nao_k04', match_maker)
        self.assertEqual(expected, actual)

    def test_fc2andzenhan(self):
        match_maker = data.MakerData()
        match_maker.matchName = 'FC2'
        match_maker.matchStr = 'FC2'
        match_maker.matchProductNumber = '[0-9]{6}'
        match_maker.replaceWords = 'PPV'
        # expected = 'FC2 PPV 868965 藻無し　【限定】清純系美少女♥調教♥中出し！　特典有り【ZIP付】'
        expected = '藻無し 【限定】清純系美少女♥調教♥中出し！ 特典有り【ZIP付】'
        copy_text = common.CopyText()
        actual = copy_text.get_title('FC2 PPV 868965 藻無し　【限定】清純系美少女♥調教♥中出し！　特典有り【ZIP付】'
                                     , '868965', match_maker)
        self.assertEqual(expected, actual)

    def test_lowercase_replace(self):
        match_maker = data.MakerData()
        match_maker.matchName = 'OKAX'
        match_maker.matchStr = ''
        match_maker.matchProductNumber = ''
        match_maker.replaceWords = ''
        expected = '日本全国のマッサージ店 美人限定 小型カメラ盗撮 4時間'
        copy_text = common.CopyText()
        actual = copy_text.get_title('okax-420 日本全国のマッサージ店 美人限定 小型カメラ盗撮 4時間'
                                     , 'OKAX-420', match_maker)

    def test_lowercase_replace_fhd(self):
        match_maker = data.MakerData()
        match_maker.matchName = 'OKAX'
        match_maker.matchStr = ''
        match_maker.matchProductNumber = ''
        match_maker.replaceWords = ''
        expected = '日本全国のマッサージ店 美人限定 小型カメラ盗撮 4時間 FHD'
        copy_text = common.CopyText()
        actual = copy_text.get_title('okax-420 日本全国のマッサージ店 美人限定 小型カメラ盗撮 4時間 FHD'
                                     , 'OKAX-420', match_maker)
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
    # test = TestCase()
    # test.main()
