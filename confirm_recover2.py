import sys
from datetime import datetime
from src import tool
from src import db
from src import common
from src import site
from src import data

jav_dao = db.jav.JavDao()
import_dao = db.import_dao.ImportDao()
maker_dao = db.maker.MakerDao()

is_checked = False
is_import = True
imports = import_dao.get_where_agreement('WHERE id = 7478')

if imports is not None:
    jav_id = imports[0].javId
    jav_where = 'WHERE id in (' + str(jav_id) + ') order by id limit 50'
else:
    # jav_where = 'WHERE id in (22980) order by id limit 50'
    jav_where = 'WHERE is_selection = 1 order by post_date '
# javs = jav_dao.get_where_agreement('WHERE is_selection = 1 and is_parse2 < 0 order by post_date ')
# javs = jav_dao.get_where_agreement('WHERE is_selection = 1 and search_result is null order by id')
# javs = jav_dao.get_where_agreement('WHERE is_selection = 1 order by id limit 100')
javs = jav_dao.get_where_agreement(jav_where)


try:
    site_collect = site.SiteInfoCollect()
    site_collect.initialize()

    site_getter = site.SiteInfoGetter(site_collect=site_collect)
except:
    print(sys.exc_info())
    exit(-1)

parser = common.AutoMakerParser(maker_dao=maker_dao)
makers = maker_dao.get_all()
recover = tool.recover.Recover(site_collect=site_collect, makers=makers)

if javs is None:
    javs = []
print('target [' + str(len(javs)) + ']')
p_tool = tool.p_number.ProductNumber(is_log_print=True)
err_list = []
ok_cnt = 0
ng_cnt = 0
for jav in javs:

    p_number, match_maker, ng_reason = p_tool.parse(jav, is_checked)
    print('【' + str(jav.id) + '】 p_number [' + p_number + '] ng_reason [' + str(ng_reason) + '] <-- [' + str(jav.isParse2) + ']' + jav.title)

    import_data = data.ImportData()
    if is_import:
        import_list = import_dao.get_where_agreement('WHERE jav_id = ' + str(jav.id))
        if import_list is None:
            print('import data nothing jav_id [' + str(jav.id) + ']')
        else:
            import_data = import_list[0]
            print('import id [' + str(import_data.id) + ']')
            if not is_checked:
                import_dao.update_p_number_info(import_data.id, p_number, match_maker)

        # site_data = data.SiteData()
        # site_data = site_getter.get_info(jav, match_maker)
        # jav_dao.update_maker_label()
        # site_data.print()

    if ng_reason > 0:
        ok_cnt = ok_cnt + 1
        if jav.sellDate is None:
            print('  no sell_date ' + jav.title)

        site_data = site_getter.get_info(jav, match_maker)

        result_search = ''
        detail = ''
        if site_data is None:
            if match_maker.name == 'SITE':
                result_search = site_getter.get_wiki(jav, match_maker)

                if len(result_search.strip()) > 0:
                    print('    site result_search [' + result_search + ']')
                    if not is_checked:
                        jav_dao.update_search_result(result_search.strip(), jav.id)
                else:
                    print('    site result not found ')
            else:
                err_list.append('id [' + str(jav.id) + '] site_data is None 【' + jav.title + '】')

        else:
            detail = site_data.get_detail()
            if not is_checked:
                jav_dao.update_detail_and_sell_date(detail, site_data.streamDate, jav.id)
                if is_import and import_data.id > 0:
                    import_dao.update_detail_and_sell_date(detail, site_data.streamDate, import_data.id)
            # site_data = data.SiteData()
            print('    site found [' + detail + ']')
            result_search = site_getter.get_wiki(jav, match_maker)
            print('    result_search [' + result_search + ']')

        # 変わった情報は更新する
        # product number
        if p_number != jav.productNumber:
            print('    change p_number [' + p_number + '] <-- [' + jav.productNumber + ']')
            if not is_checked:
                jav_dao.update_product_number(jav.id, p_number)

        # detail
        is_changed = False
        if detail is not None and len(detail) > 0:
            sell_date = None
            if site_data is not None:
                str_sell_date = site_data.streamDate
                # maker.registeredBy = 'AUTO ' + datetime.now().strftime('%Y-%m-%d')
                try:
                    sell_date = datetime.strptime(str_sell_date, '%Y/%m/%d')
                except:
                    pass

            if sell_date is not None:
                if jav.sellDate is None:
                    jav.sellDate = datetime.strptime('1900-01-01', '%Y-%m-%d')
                if sell_date.strftime('%Y-%m-%d') != jav.sellDate.strftime('%Y-%m-%d'):
                    is_changed = True
                    print('    change sell_date ' + sell_date.strftime('%Y-%m-%d') + ' <- '
                          + jav.sellDate.strftime('%Y-%m-%d'))

            jav_detail = ''
            if jav.detail is not None:
                jav_detail = jav.detail.strip()
            if detail.strip() != jav_detail.strip():
                is_changed = True
                print('    change detail ' + detail + ' <- ' + jav_detail)

            if not is_checked and is_changed:
                jav_dao.update_detail_and_sell_date(detail, site_data.streamDate, jav.id)

        # isParse2 ( ng_reason )
        if jav.isParse2 != ng_reason:
            if not is_checked:
                jav_dao.update_checked_ok(ng_reason, match_maker.id, jav)
            else:
                print('    change ng_reason')

        # searchResult ( result_search )
        if jav.searchResult is None:
            jav_searchResult = ''
        else:
            jav_searchResult = jav.searchResult.strip()
        if result_search.strip() != jav_searchResult:
            if not is_checked:
                jav_dao.update_search_result(result_search.strip(), jav.id)
            else:
                print('    change search_result [' + result_search + '] <-- [' + jav_searchResult + ']')

        if is_import and import_data.id > 0:
            if not is_checked:
                import_list = import_dao.update_search_result(result_search.strip(), import_data.id)
            print('import result search [' + result_search + ']')

    else:
        try:
            new_maker, site_data = recover.get_ng_new_maker(p_number, ng_reason, jav)
            if new_maker is not None:
                new_maker.print('NEW ')
                if not is_checked:
                    maker_dao.export(new_maker)
        except tool.recover.RecoverError as rerr:
            err_list.append(str(rerr))

for err in err_list:
    print(err)

