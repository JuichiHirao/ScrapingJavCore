from mysql.connector.errors import DataError
from datetime import datetime
from src import tool
from src import db
from src import common
from src import site
from src import data
import sys
import traceback

jav_dao = db.jav.JavDao()
import_dao = db.import_dao.ImportDao()
maker_dao = db.maker.MakerDao()
import_parser = common.ImportParser()

# is_checked = True
is_checked = False
# is_import = True
is_import = False
# imports = import_dao.get_where_agreement('WHERE id = -1')

imports = import_dao.get_where_agreement('WHERE id = 8658 and filename like \'%【FC2%\'')
imports = None

if is_import:
    # imports = import_dao.get_where_agreement('WHERE id > 18000 and length(filename) <= 0')
    # imports = import_dao.get_where_agreement('WHERE id > 18000')
    imports = import_dao.get_where_agreement('WHERE id = 21825')

if imports is not None:
    if len(imports) == 1:
        jav_id_in = imports[0].javId
    else:
        jav_id_in = imports[0].javId
        for import_data in imports[1:]:
            if import_data.javId > 0:
                jav_id_in = '{}, {}'.format(jav_id_in, import_data.javId)
    javs = jav_dao.get_where_agreement('WHERE id in ({})'.format(jav_id_in))
    # print(len(javs))
    # exit(-1)
else:
    # jav_where = 'WHERE id in (69659, 69660, 69661, 69662, 70953) order by id limit 50'
    # jav_where = 'WHERE id in (75227) order by id limit 50'
    # jav_where = 'WHERE id in (9948) order by id limit 50'
    # jav_where = 'WHERE is_parse2 < 0 and is_selection = 1 order by post_date '
    # jav_where = 'WHERE is_selection = 0 and post_date >= "2020-04-17 08:50:00" order by post_date '
    # jav_where = 'WHERE is_selection = 1 and post_date >= "2020-07-01 08:50:00" order by post_date '
    # jav_where = 'WHERE is_selection in (0, 1) and post_date >= "2020-04-25 12:00:00" order by post_date '
    jav_where = 'WHERE is_selection in (0) and post_date >= (select post_date from jav where id = 75227) order by post_date '
    # jav_where = 'WHERE is_selection = 1 and post_date >= "2020-05-01 12:00:00" and makers_id != 835 order by post_date '
    # jav_where = 'WHERE is_selection = 1 and post_date >= "2020-03-16 12:00:00" and makers_id != 835 order by post_date '
    # javs = jav_dao.get_where_agreement('WHERE is_selection = 1 and is_v   parse2 < 0 order by post_date ')
    # javs = jav_dao.get_where_agreement('WHERE is_selection = 1 and search_result is null order by id')
    # javs = jav_dao.get_where_agreement('WHERE is_selection = 1 order by id limit 100')
    javs = jav_dao.get_where_agreement(jav_where)


parser = common.AutoMakerParser(maker_dao=maker_dao)

site_getter = None
try:
    site_collect = site.SiteInfoCollect()
    site_collect.initialize()

    site_getter = site.SiteInfoGetter(site_collect=site_collect, is_debug=True)
except:
    print(sys.exc_info())
    exit(-1)

if site_getter is None:
    print('site_getter is None')
    exit(-1)

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
        # if site_data:
        #     site_data.print()

    actress_name = ''
    is_changed_p_number = False
    if ng_reason > 0:
        ok_cnt = ok_cnt + 1
        if jav.sellDate is None:
            print('  no sell_date ' + jav.title)

        if jav.productNumber != p_number:
            jav.productNumber = p_number
            is_changed_p_number = True

        site_data = site_getter.get_info(jav, match_maker)

        result_search = ''
        detail = ''
        actress_name = ''
        is_selldate_changed = False
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
                try:
                    jav_dao.update_detail_and_sell_date(detail, site_data.streamDate, jav.id)
                    if is_import and import_data.id > 0:
                        import_data.detail = detail
                        import_data.sellDate = site_data.streamDate
                        # import_dao.update_detail_and_sell_date(detail, site_data.streamDate, import_data.id)
                except DataError as de:
                    print(str(de))
                    print(traceback.format_exc())
                    exit(-1)
            # site_data = data.SiteData()
            print('    site found [' + detail + ']')
            result_search = site_getter.get_wiki(jav, match_maker)
            print('    result_search [' + result_search + ']')

            if is_import and import_data.id > 0:
                import_data.searchResult = result_search

            wiki_detail_data = site_getter.get_contents_info(jav, result_search)

            if wiki_detail_data is not None:
                actress_name = wiki_detail_data.actress
                if jav.sellDate is None:
                    if len(wiki_detail_data.streamDate) > 0:
                        print('sell_date ' + wiki_detail_data.streamDate)
                        is_selldate_changed = True
                # jav_dao.update_actress(jav.id, actress_name)
                # import_data.tag = actress_name

        # 変わった情報は更新する
        # actress
        jav.actress = jav.actress.replace('—-', '')
        if len(actress_name) > 0 >= len(jav.actress):
            print('    change actress [' + actress_name + '] <-- [' + jav.actress + ']')
            if not is_checked:
                jav_dao.update_actress(jav.id, actress_name)
            if is_import and import_data.id > 0:
                import_data.tag = actress_name
        else:
            if len(actress_name) > 0 and len(jav.actress.strip()) > 0:
                msg = '【{}】 already set actress [{}] get_info [{}]'.format(jav.productNumber, jav.actress, actress_name)
                print(msg)
                err_list.append(msg)

        # product number
        if is_changed_p_number:
            print('    change p_number [' + p_number + '] <-- [' + jav.productNumber + ']')
            if not is_checked:
                jav_dao.update_product_number(jav.id, p_number)
        if is_import and import_data.id > 0:
            if p_number != import_data.productNumber:
                print('    change import p_number [' + p_number + '] <-- [' + import_data.productNumber + ']')
                import_data.productNumber = jav.productNumber

        # detail
        is_changed = False
        if (detail is not None and len(detail) > 0) or is_selldate_changed:
            sell_date = None
            if is_selldate_changed:
                try:
                    if '-' in wiki_detail_data.streamDate:
                        sell_date = datetime.strptime(wiki_detail_data.streamDate, '%Y-%m-%d')
                    else:
                        sell_date = datetime.strptime(wiki_detail_data.streamDate, '%Y/%m/%d')
                except:
                    pass
            else:
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

        # if is_import and import_data.id > 0:
        #     if not is_checked:
        #         import_list = import_dao.update_search_result(result_search.strip(), import_data.id)
        #     print('import result search [' + result_search + ']')

        # FC2 label
        if match_maker is not None and (match_maker.id == 835 or match_maker.id == 255):
            if site_data is not None and jav.label != site_data.maker:
                if not is_checked:
                    import_data.maker = match_maker.get_maker(site_data.maker)
                    import_data.filename = import_parser.get_filename(import_data)
                    jav_dao.update_maker_label(jav.maker, site_data.maker, jav.id)
                    import_dao.update(import_data)
                else:
                    print('    change fc2 label [' + site_data.maker + ']')
        else:
            if is_import and not is_checked:
                import_dao.update(import_data)

        if ng_reason == -4 and len(jav.maker) > 0:
            try:
                new_maker, site_data = recover.get_ng_new_maker(p_number, ng_reason, jav)
                if new_maker is not None:
                    new_maker.print('NEW ')
                    if not is_checked:
                        maker_dao.export(new_maker)
                    makers.append(new_maker)
            except tool.recover.RecoverError as rerr:
                err_list.append(str(rerr))
    else:
        try:
            new_maker, site_data = recover.get_ng_new_maker(p_number, ng_reason, jav)
            if new_maker is not None:
                new_maker.print('NEW ')
                if not is_checked:
                    maker_dao.export(new_maker)
                makers.append(new_maker)
        except tool.recover.RecoverError as rerr:
            err_list.append(str(rerr))

for err in err_list:
    print(err)

