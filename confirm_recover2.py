from src import tool
from src import db
from src import common
from src import site
from src import data

jav_dao = db.jav.JavDao()
import_dao = db.import_dao.ImportDao()
maker_dao = db.maker.MakerDao()

javs = jav_dao.get_where_agreement('WHERE is_selection = 1 order by id')
# javs = jav_dao.get_where_agreement('WHERE is_selection = 1 and search_result is null order by id')
# javs = jav_dao.get_where_agreement('WHERE is_parse2 <= 0 and is_selection = 1 order by id')
# javs = jav_dao.get_where_agreement('WHERE id in (19816) order by id limit 50')

site_collect = site.SiteInfoCollect()
site_collect.initialize()

site_getter = site.SiteInfoGetter(site_collect=site_collect)

parser = common.AutoMakerParser(maker_dao=maker_dao)
makers = maker_dao.get_all()
recover = tool.recover.Recover(site_collect=site_collect, makers=makers)

if javs is None:
    javs = []
print('target [' + str(len(javs)) + ']')
p_tool = tool.p_number.ProductNumber(is_log_print=False)
err_list = []
ok_cnt = 0
ng_cnt = 0
is_checked = True
is_import = False
for jav in javs:

    p_number, match_maker, ng_reason = p_tool.parse(jav, is_checked)
    print('p_number [' + p_number + '] ng_reason [' + str(ng_reason) + ']')

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
        # p_tool.get_log_print()
        ok_cnt = ok_cnt + 1
        if not is_checked:
            jav_dao.update_checked_ok(ng_reason, match_maker.id, jav)

        if jav.sellDate is None:
            print('no sell_date ' + jav.title)

        site_data = site_getter.get_info(jav, match_maker)

        result_search = ''
        if site_data is None:
            err_list.append('id [' + str(jav.id) + '] site_data is None 【' + jav.title + '】')

            if match_maker.name == 'SITE':
                result_search = site_getter.get_wiki(jav, match_maker)
        else:
            detail = site_data.get_detail()
            if not is_checked:
                jav_dao.update_detail_and_sell_date(detail, site_data.streamDate, jav.id)
                if is_import and import_data.id > 0:
                    import_dao.update_detail_and_sell_date(detail, site_data.streamDate, import_data.id)
            # site_data = data.SiteData()
            print('site found [' + detail + ']')
            result_search = site_getter.get_wiki(jav, match_maker)
            print('result_search [' + result_search + ']')
            if not is_checked:
                jav_dao.update_search_result(result_search.strip(), jav.id)

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

