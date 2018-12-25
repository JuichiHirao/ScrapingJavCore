from src import site
from src import common
from src import db

# mgs = site.mgs.Mgs()
# detail, sell_date = mgs.get_info('277DCV-093')
# detail, sell_date = mgs.test_execute()
# print(' [' + str(sell_date) + '] ' + detail)

jav_dao = db.jav.JavDao()
javs = jav_dao.get_where_agreement('WHERE id = 11598')
# javs = jav_dao.get_where_agreement('WHERE id = 13612')
parser = common.AutoMakerParser()
maker = parser.get_maker(javs[0])
maker.print()
