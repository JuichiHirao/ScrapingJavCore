from src import site
from src import tool
from src import db

jav_dao = db.jav.JavDao()
import_dao = db.import_dao.ImportDao()
# maker_dao = db.maker.MakerDao()

# makers = maker_dao.get_all()
google = site.wiki.Google()
mgs = site.mgs.Mgs()

# javs = jav_dao.get_where_agreement('WHERE is_selection = 1 limit 20')
'''
fanza = site.fanza.Fanza()
p_tool = tool.p_number.ProductNumber()
# p_number, seller, sell_date, match_maker, ng_reason = p_tool.parse_and_fc2(javs[0], True)
site_data = fanza.get_info('SDMU-912')
# site_data.print()
'''

'''
for jav in javs:
    google.get_info(javs[0].productNumber)
'''

import_list = import_dao.get_where_agreement('WHERE id = 5444')
for import_data in import_list:
    if '[裏' in import_data.filename:
        print('URA not target')
        continue

    if len(import_data.filename) <= 0:
        print('filename is not setting')
        continue

    site_name, site_url = google.get_info(import_data.productNumber)
    search_result = site_name + ' ' + site_url
    # print('result ' + site_name + ' ' + site_url)
    # print('search_result ' + import_data.searchResult)

    # if import_data.searchResult is not None and 'no search result' in import_data.searchResult:
    import_dao.update_search_result(search_result, import_data.id)

    '''
        filter_makers = list(filter(lambda maker:
                                         len(maker.matchProductNumber.strip()) > 0
                                         and len(maker.matchStr) > 0, self.makers))
    '''

