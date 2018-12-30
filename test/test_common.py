import unittest
from src import common
from src import data

# PYTHONPATH=. python test/test_common.py -v
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

    def test_hankaku_slash(self):
        match_maker = data.MakerData()
        match_maker.matchName = '300MIUM'
        match_maker.matchStr = ''
        match_maker.matchProductNumber = ''
        match_maker.replaceWords = ''
        expected = '働くドMさん. Case.2 健康食品メーカー経理／加藤さん／23歳 早口で捲し立てるも断りきれないド真面目OL！！'
        copy_text = common.CopyText()
        actual = copy_text.get_title('300MIUM-329 働くドMさん. Case.2 健康食品メーカー経理/加藤さん/23歳 早口で捲し立てるも断りきれないド真面目OL！！'
                                     , '300MIUM-329', match_maker)
        self.assertEqual(expected, actual)

    def test_h0930(self):
        match_maker = data.MakerData()
        match_maker.name = 'エッチなオクサマ H0930'
        match_maker.matchName = 'エッチなオクサマ H0930'
        match_maker.matchStr = 'H0930|エッチな0930'
        match_maker.matchProductNumber = 'ori[0-9][0-9][0-9][0-9]|pla[0-9]{4}|gol[0-9]{3}|ki[1-2][5-9][0-9]{4}'
        # match_maker.replaceWords = 'エッチな0930¥t[a-zA-Z ]*¥t/[0-9]{2}[歳才]/ /'
        match_maker.replaceWords = 'エッチな0930¥t[a-zA-Z ]*¥t/(?P<age>[0-9]{2}[歳才])/ age/'
        expected = '藤本かおり 31歳'
        copy_text = common.CopyText()
        actual = copy_text.get_title('H0930 ki181021 エッチな0930 藤本 かおり Kaori Fu jimoto 31歳'
                                     , 'ki181021', match_maker)
        self.assertEqual(expected, actual)

    # jav.titleがmaker.match_strに存在しない場合
    def test_nomatch_maker(self):
        jav_data = data.JavData()
        jav_data.maker = 'てきとうめーかー'
        jav_data.title = 'ABCD-9912 TESTTESTTEST'
        parser = common.AutoMakerParser()
        actual = parser.get_maker(jav_data)

        expected = 'ABCD'
        self.assertEqual(expected, actual.matchStr)
        expected = 'てきとうめーかー'
        self.assertEqual(expected, actual.matchName)


if __name__ == "__main__":
    unittest.main()
