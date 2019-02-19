from src import site
from src import db

# import_dao = db.import_dao.ImportDao()
jav_dao = db.jav.JavDao()
maker_dao = db.maker.MakerDao()

google = site.wiki.Google()
site_info = site.wiki.Site()
mgs = site.mgs.Mgs()

'''
import_list = import_dao.get_where_agreement('WHERE id = 5750')
for import_data in import_list:
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
makers = maker_dao.get_all()

javs = jav_dao.get_where_agreement('WHERE id = 17603')
for jav in javs:

    if jav.makersId > 0:
        match_makers = list(filter(lambda maker:
                             maker.id == jav.makersId, makers))
        if len(match_makers) > 0:
            site_name, site_url = site_info.get_info(match_makers[0])
            print('result ' + site_name + ' ' + site_url)
