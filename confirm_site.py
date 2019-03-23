from src import site
from src import db
from src import data
from src import common

site_collect = site.SiteInfoCollect()
site_collect.initialize()
site_getter = site.SiteInfoGetter(site_collect=site_collect)
import_parser = common.ImportParser()

import_dao = db.import_dao.ImportDao()
jav_dao = db.jav.JavDao()
maker_dao = db.maker.MakerDao()

makers = maker_dao.get_all()

import_list = import_dao.get_where_agreement('WHERE id = 6630')
for import_data in import_list:
    javs = jav_dao.get_where_agreement('WHERE id = ' + str(import_data.javId))

    if javs is None:
        print('match jav none [' + str(import_data.javId) + ']')
        continue

    match_jav = javs[0]

    match_makers = list(filter(lambda maker: maker.id == match_jav.makersId, makers))

    if javs is None:
        print('match jav none [' + str(import_data.javId) + ']')
        continue

    match_maker = match_makers[0]

    # maker_id 835 FC2
    if match_jav.makersId == 835:
        if match_jav.label is not None and len(match_jav.label) > 0:
            pass
        else:
            site_data = data.SiteData()
            site_data = site_getter.get_info(match_jav, match_makers[0])

            if site_data is not None:
                site_data.print()
                # get_title(self, copy_text: str = '', product_number: str = '', match_maker: data.MakerData = None):
                if match_jav.label != site_data.maker:
                    print('change label [' + site_data.maker + '] <-- [' + match_jav.label + ']')
                    match_jav.label = site_data.maker
                    import_data.maker = match_maker.get_maker(match_jav.label)
                    print('maker:label [' + match_makers[0].get_maker(site_data.maker) + ']')
                    # filename = site_collect.copy_text.get_title(match_jav.title, match_jav.productNumber, match_makers[0])
                    import_data.filename = import_parser.get_filename(import_data)
                    print('filename ' + import_data.filename)
                    jav_dao.update_maker_label(match_maker.name, match_jav.label, match_jav.id)
                    import_dao.update_maker_and_filename(import_data.id, import_data.maker, import_data.filename)
            else:
                print('not site_data')
    else:
            print('not fc2')

'''
    if '[裏' in import_data.filename:
        print('URA not target')
        continue

    if len(import_data.filename) <= 0:
        print('filename is not setting')
        continue

    if 'SITE：' in import_data.filename:
        site_name, site_url = site_info.get_info()
    site_name, site_url = google.get_info(import_data.productNumber)
    search_result = site_name + ' ' + site_url
    # print('result ' + site_name + ' ' + site_url)
    # print('search_result ' + import_data.searchResult)
'''


'''
javs = jav_dao.get_where_agreement('WHERE id = 17603')
for jav in javs:

    if jav.makersId > 0:
        match_makers = list(filter(lambda maker:
                             maker.id == jav.makersId, makers))
        if len(match_makers) > 0:
            site_name, site_url = site_info.get_info(match_makers[0])
            print('result ' + site_name + ' ' + site_url)
'''
