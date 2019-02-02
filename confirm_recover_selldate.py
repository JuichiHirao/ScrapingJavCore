import urllib
from src import site
from src import tool
from src import db
from src import common

jav_dao = db.jav.JavDao()
maker_dao = db.maker.MakerDao()

copytext = common.CopyText()
fc2 = site.fc2.Fc2()
mgs = site.mgs.Mgs()
hey = site.hey.Hey()
wiki = site.wiki.SougouWiki()
google = site.wiki.Google()
fanza = site.fanza.Fanza()
# javs = jav_dao.get_where_agreement('WHERE is_selection = 1 '
#                                    'order by post_date limit 80')
javs = jav_dao.get_where_agreement('WHERE is_selection = 1 and (sell_date is null or sell_date = \'1900-01-01\') '
                                   'order by post_date ')
# javs = jav_dao.get_where_agreement('WHERE id = 16247')
# javs = jav_dao.get_where_agreement('WHERE is_parse2 <= 0 and is_selection = 1 and id <= 17143 order by id limit 50')

# parser = common.AutoMakerParser()
makers = maker_dao.get_all()

if javs is None:
    javs = []
print('target [' + str(len(javs)) + ']')
p_tool = tool.p_number.ProductNumber(is_log_print=False)
err_list = []
ok_cnt = 0
ng_cnt = 0
is_checked = True
for jav in javs:
    print('[' + str(jav.id) + ']' + jav.title)

    site_data = None
    find_filter_maker = filter(lambda maker: maker.id == jav.makersId, makers)
    find_maker_list = list(find_filter_maker)
    if len(find_maker_list) <= 0:
        err_list.append('not found[' + str(jav.id) + ']  ' + str(jav.makersId))
        ng_cnt = ng_cnt + 1
        continue

    match_maker = find_maker_list[0]
    print('[' + str(jav.id) + ']  p_num [' + jav.productNumber + ']' + match_maker.name)

    if match_maker.name == 'HEY動画':
        site_data = hey.get_info(jav.productNumber)

        if site_data is None:
            err_list.append('HEY動画 not found[' + str(jav.id) + ']  ' + match_maker.label)
            ng_cnt = ng_cnt + 1
            continue

        print(site_data.streamDate + '  ' + site_data.maker)

    elif match_maker.name == 'MGS':
        site_data = mgs.get_info(jav.productNumber)

        if site_data is None:
            err_list.append('MGS not found[' + str(jav.id) + ']  ' + jav.title)
            detail = 'no mgs result'
            ng_cnt = ng_cnt + 1
            continue

        print(site_data.streamDate + '  ' + site_data.maker)

    elif match_maker.name == 'FC2 コンテンツマーケット':
        site_data = fc2.get_info(jav.productNumber)

        if site_data is None:
            err_list.append('FC2 not found[' + str(jav.id) + ']  ' + jav.title)
            ng_cnt = ng_cnt + 1
            continue

        print(site_data.streamDate + '  ' + site_data.maker)

    elif match_maker.name == 'SITE':
        print('SITE DAYO ' + jav.title)
        ng_cnt = ng_cnt + 1
        continue

    else:
        if match_maker.kind == 1:
            site_data = fanza.get_info(jav.productNumber)

            if site_data is None:
                err_list.append('FANZA not found[' + str(jav.id) + ']  ' + jav.title)
                ng_cnt = ng_cnt + 1
                continue
        else:
            print('URA DAYO ' + jav.title)

    if match_maker.kind == 3:
        if site_data is not None:
            # is_siteも1に更新
            try:
                jav_dao.update_site_info(site_data.maker, site_data.streamDate, jav.id)
            except:
                site_data.print('Error ')
                ng_cnt = ng_cnt + 1
                # exit(-1)
            ok_cnt = ok_cnt + 1
        else:
            str_date = copytext.get_date_ura(jav.title)
            if len(str_date) > 0:
                jav_dao.update_detail_and_sell_date('', str_date, jav.id)
                ok_cnt = ok_cnt + 1
            else:
                print('site_data is None date not found' + jav.title)
                ng_cnt = ng_cnt + 1
    # if match_maker.kind == 3:
    else:
        if site_data is not None:
            detail = site_data.get_detail()
            # if jav.maker is None or len(jav.maker) <= 0:
            #     jav_dao.update_maker_label(match_maker.name, match_maker.label, jav.id)
            # is_siteも1に更新
            jav_dao.update_detail_and_sell_date(detail, site_data.streamDate, jav.id)

            if jav.searchResult is None or len(jav.searchResult.strip()) <= 0:
                print('searchResult [' + jav.productNumber + ']')
                searchResult = ''
                try:
                    site_name, site_url = google.get_info(jav.productNumber)
                    if len(site_name) > 0:
                        searchResult = site_name + ' ' + site_url
                except urllib.error.HTTPError as err:
                    print('HTTP Error pNumber [' + jav.productNumber + ']')

                if len(searchResult) <= 0:
                    searchResult = 'no search result'

                jav_dao.update_search_result(searchResult, jav.id)

            ok_cnt = ok_cnt + 1
        # if site_data is not None:
        else:
            print('site_data is None ' + jav.title)
            ng_cnt = ng_cnt + 1

for err in err_list:
    print(err)

print('ok [' + str(ok_cnt) + ']')
print('ng [' + str(ng_cnt) + ']')
