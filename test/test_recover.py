import unittest
from src import common
from src import data
from src import tool


# PYTHONPATH=. python test/test_common.py -v
class TestRecover(unittest.TestCase):

    def setUp(self):
        makers = []
        maker = data.MakerData()
        maker.matchName = 'FC2'
        maker.matchStr = 'FC2'
        maker.matchProductNumber = '[0-9]{6}'
        maker.replaceWords = 'PPV'
        makers.append(maker)

        maker = data.MakerData()
        maker.name = 'HEY動画'
        maker.matchName = 'AV9898'
        maker.label = 'AV9898'
        maker.matchLabel = 'AV9898'
        maker.kind = 'AV9898'
        maker.matchStr = '(4030|AV9898)'
        maker.matchProductNumber = 'PPV[0-9]{4}'
        maker.replaceWords = 'PPV'
        maker.pNumberGen = 1
        makers.append(maker)

        maker = data.MakerData()
        maker.name = 'ゲインコーポレーション'
        maker.matchName = 'ゲインコーポレーション'
        maker.label = 'gain corporation'
        maker.matchLabel = 'gain corporation'
        maker.kind = '1'
        maker.matchStr = 'TITG'
        makers.append(maker)

        self.recover = tool.recover.Recover(makers=makers)

    def test_ng_new_maker_minus1(self):
        jav = data.JavData()

        jav.title = 'MYAB-004 TESTTESTTES'
        jav.productNumber = 'MYAB-004'
        jav.maker = 'Maker Name'
        new_maker = self.recover.get_ng_new_maker('MYAB-004', -1, jav)

        self.assertEqual('Maker Name', new_maker.name)

    '''
    def test_ng_new_maker_minus4(self):
        # 14928 SHE-626
        jav = data.JavData()

        jav.title = 'SHE-626 KIRE'
        jav.productNumber = 'SHE-626'
        jav.maker = 'Maker Name'
        new_maker = self.recover.get_ng_new_maker(-1, jav)
    '''

        # self.assertEqual('Maker Name', new_maker.name)

    def test_ng_new_maker_minus21_hey_raise_not_site_info(self):
        #   -21 : タイトル内にpNumberは存在したが、一致するメーカーは存在しない
        jav = data.JavData()

        jav.title = 'TEST 4999-9999 える！ガル！転落'
        jav.productNumber = '4999-9999'
        jav.maker = 'Maker Name'
        with self.assertRaises(tool.recover.RecoverError) as cm:
            self.recover.get_ng_new_maker('4999-9999', -21, jav)

        self.assertEqual(cm.exception.args[0], '-21でHEYのサイトで詳細が存在しないため発生')

    def test_ng_new_maker_minus21_hey_raise_maker_exist(self):
        #   -21 : タイトル内にpNumberは存在したが、一致するメーカーは存在しない
        jav = data.JavData()

        jav.title = 'av9898 4030-2075 える！ガル！転落'
        jav.productNumber = '4030-2075'
        jav.maker = 'Maker Name'
        with self.assertRaises(tool.recover.RecoverError) as cm:
            self.recover.get_ng_new_maker('4030-2075', -21, jav)

        self.assertEqual(cm.exception.args[0], '-21でHEYでmakerに同様の提供元が存在で発生')

    def test_ng_new_maker_minus21_mgs_exist(self):
        #   -21 : タイトル内にpNumberは存在したが、一致するメーカーは存在しない
        jav = data.JavData()

        jav.title = '326MEM-009 RURU'
        jav.productNumber = '326MEM-009'
        new_maker = self.recover.get_ng_new_maker('326MEM-009', -21, jav)
        new_maker.print('NEW ')

        self.assertEqual('MGS', new_maker.name)
        self.assertEqual('黒船', new_maker.label)

    def test_ng_new_maker_minus21_mgs_not_exist(self):
        #   -21 : タイトル内にpNumberは存在したが、一致するメーカーは存在しない
        # FANZAから取得出来るメーカー名とレーベルが同じ場合は、レーベル名を消す
        jav = data.JavData()

        jav.title = 'DACV-085 40NIN 8ZIKAN'
        jav.productNumber = 'DACV-085'
        new_maker = self.recover.get_ng_new_maker('DACV-085', -21, jav)
        new_maker.print('NEW ')

        self.assertEqual('センタービレッジ', new_maker.name)
        self.assertEqual('', new_maker.label)

    def test_ng_new_maker_minus21_fanza_same_raise(self):
        #   -21 : タイトル内にpNumberは存在したが、一致するメーカーは存在しない
        # FANZAから取得出来るメーカー名とレーベルが同じ場合は、レーベル名を消す
        jav = data.JavData()

        jav.title = 'TITG-014 SOKU RUI'
        jav.productNumber = 'TITG-014'

        with self.assertRaises(tool.recover.RecoverError) as cm:
            new_maker = self.recover.get_ng_new_maker('TITG-014', -21, jav)
            new_maker.print('NEW ')

        self.assertEqual(cm.exception.args[0], 'new_makerのmatch_strは既にscraping.makerに存在')


if __name__ == "__main__":
    unittest.main()
