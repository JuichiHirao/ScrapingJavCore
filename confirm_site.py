from src import site
from src import db
from src import data
from src import common
from src import tool

from datetime import datetime

site_collect = site.SiteInfoCollect()
site_collect.initialize()
site_getter = site.SiteInfoGetter(site_collect=site_collect)
import_parser = common.ImportParser()

import_dao = db.import_dao.ImportDao()
jav_dao = db.jav.JavDao()
maker_dao = db.maker.MakerDao()

p_tool = tool.p_number.ProductNumber()
copy_text_tool = common.CopyText()

makers = maker_dao.get_all()

# is_checked = True
is_checked = False

# import_list = import_dao.get_where_agreement('WHERE id = 6764')
import_list = import_dao.get_where_agreement('WHERE id = 7855')
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

    # if match_maker.kind != 1:
    #     continue

    p_number = p_tool.get_registered_p_number(match_jav, match_maker)
    if p_number == import_data.productNumber:
        print('match p_number [' + p_number + '] import [' + import_data.productNumber + '] jav [' + match_jav.productNumber + ']')
    else:
        print('change p_number [' + p_number + '] <--- [' + import_data.productNumber + '] jav [' + match_jav.productNumber + ']')
        if not is_checked:
            import_dao.update_p_number_info(import_data.id, p_number, match_maker)

    detail = ''
    # p_number, match_maker, ng_reason = p_tool.parse(match_jav)
    site_data = site_getter.get_info(match_jav, match_maker)
    # print(str(match_jav.sellDate))
    # site_data.print()
    # site_data = data.SiteData()

    if site_data is not None:
        detail = site_data.get_detail()
    else:
        print('SiteData is None')

    if import_data.detail is not None:
        import_detail = import_data.detail
    else:
        import_detail = ''
    if import_detail != detail:
        print('change ' + detail + ' <-- ' + import_detail)
        import_data.detail = detail
        # sell_date = datetime.strptime(site_data.streamDate, '%y%m%d%y')
        # str_date = sell_date.strftime('%Y-%m-%d')
        import_data.sellDate = site_data.streamDate
        if not is_checked:
            jav_dao.update_detail_and_sell_date(detail, site_data.streamDate, import_data.javId)
            import_dao.update_detail_and_sell_date(site_data.get_detail(), site_data.streamDate, import_data.id)

    import_data.title = copy_text_tool.get_title(match_jav.title, match_jav.productNumber, match_maker)
    import_data.filename = import_parser.get_filename(import_data)
    print('filename ' + import_data.filename)

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
                    import_data.filename = import_parser.get_filename(import_data)
                    print('filename ' + import_data.filename)
                    jav_dao.update_maker_label(match_maker.name, match_jav.label, match_jav.id)
            else:
                print('not site_data')
    else:
            print('not fc2')

    if not is_checked:
        import_dao.update(import_data)

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
