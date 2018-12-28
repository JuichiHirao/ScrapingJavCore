from src import site
from src import common
from src import db

jav_dao = db.jav.JavDao()
mgs = site.mgs.Mgs()

# javs = jav_dao.get_where_agreement('WHERE id = 13715') # 326SPOR-002
# javs = jav_dao.get_where_agreement('WHERE id = 13711') # 348NTR-001
# javs = jav_dao.get_where_agreement('WHERE id = 13918') # 326EVA-007
javs = jav_dao.get_where_agreement('WHERE id = 13917') # 326SPOR-001
site_data = mgs.get_info(javs[0].productNumber)
site_data.print()

parser = common.AutoMakerParser()
maker = parser.get_maker_from_site(site_data, 'MGS')
maker.print()
'''
exist_flag = mgs.exist_product_number('300MIUM-365')
print('300MIUM-365    ' + str(exist_flag))
exist_flag = mgs.exist_product_number('300MIUM-365123')
print('300MIUM-365123 ' + str(exist_flag))

site_data = mgs.get_info('300MIUM-365')
site_data.print()
'''

parser = common.AutoMakerParser()
maker = parser.get_maker_from_site(site_data, 'MGS')
maker.print()
# detail, sell_date = mgs.test_execute()
# print(' [' + str(sell_date) + '] ' + detail)

# javs = jav_dao.get_where_agreement('WHERE id = 13715')
# javs = jav_dao.get_where_agreement('WHERE id = 11598')
# javs = jav_dao.get_where_agreement('WHERE id = 13612')
# parser = common.AutoMakerParser()
# maker = parser.get_maker(javs[0])
# maker.print()

