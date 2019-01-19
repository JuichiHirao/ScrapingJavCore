from src import site
from src import tool
from src import db
from src import common

jav_dao = db.jav.JavDao()
maker_dao = db.maker.MakerDao()

# fc2 = site.fc2.Fc2()
mgs = site.mgs.Mgs()
hey = site.hey.Hey()
fanza = site.fanza.Fanza()
# javs = jav_dao.get_where_agreement('WHERE is_parse2 <= 0 and is_selection = 1 order by id limit 50')
javs = jav_dao.get_where_agreement('WHERE is_parse2 <= 0 and is_selection = 1 and id <= 16546 order by id limit 50')

parser = common.AutoMakerParser()

print('target [' + str(len(javs)) + ']')
p_tool = tool.p_number.ProductNumber(is_log_print=False)
err_list = []
ok_cnt = 0
ng_cnt = 0
is_checked = False
for jav in javs:

    match_maker, ng_reason = p_tool.parse(jav, is_checked)

    if ng_reason > 0:
        p_tool.get_log_print()
        ok_cnt = ok_cnt + 1
        if not is_checked:
            jav_dao.update_checked_ok(ng_reason, match_maker.id, jav)

        if jav.sellDate is None:
            print('no sell_date ' + jav.title)

    else:
        new_maker = None
        err_list.append(str(jav.id) + ' [' + str(ng_reason) + '] ' + jav.title)
        err_list.append('    ' + str(p_tool.get_log_print()))
        ng_cnt = ng_cnt + 1
        # -1 : メーカー名に一致するmaker無し
        # -3 : メーカー一致が複数件、match_strに一致するmaker無し
        #   メーカーに登録
        # -2 : メーカー名1件だけ完全一致したが、match_strの文字列がtitleにない
        #   match_strに完全一致のメーカーをdelete:1にして、新規としてメーカーに登録
        if ng_reason == -1 or ng_reason == -2 or ng_reason == -3:
            if ng_reason == -2:
                # err_list.append('-2発生、1件一致の[' + jav.productNumber + ']deletedを1にする必要あり')

                # deleted : 1 に更新
                arr_match_str = jav.productNumber.split('-')
                makers = maker_dao.get_where_agreement('WHERE match_str = %s', (arr_match_str[0]))
                if makers is not None and len(makers) == 1:
                    if not is_checked:
                        maker_dao.update_deleted(1, makers[0])
                else:
                    err_list.append('-2発生、1件一致のmaker [' + jav.productNumber + '] 発見できず')
            try:
                new_maker = parser.get_maker(jav)
                # new_maker.print()
                p_tool.append_maker(new_maker)
            except common.MatchStrSameError as err:
                print(str(err))

        #   -21 : タイトル内にpNumberは存在したが、一致するメーカーは存在しない
        p_number = ''
        if ng_reason == -21:
            hey_p_number, hey_label = p_tool.get_p_number_hey(jav.title)

            if len(hey_p_number) > 0:

                err_list.append('      [' + hey_p_number + '] 【' + hey_label + '】')
                site_data = hey.get_info(hey_p_number)
                if site_data is None or len(site_data.maker) <= 0:
                    err_list.append('      HEYのp_number[ ' + hey_p_number + ']だが、HEYには存在しない ' + jav.title)
                    continue

                makers = maker_dao.get_where_agreement('WHERE label = %s', (site_data.maker, ))

                if makers is not None:
                    err_list.append('      【' + site_data.maker + '】はmakerに存在 maker_id [' + str(makers[0].id))
                    continue

                err_list.append('      [' + site_data.streamDate + '] 【' + site_data.maker + '】')
                new_maker = parser.get_maker_hey(hey_p_number, site_data)
                p_number = hey_p_number

            else:
                p_number = p_tool.get_maker_match_number(None, jav.title)
                site_data = mgs.get_info(p_number)

                site_name = 'MGS'
                if site_data is None or len(site_data.productNumber) <= 0:
                    err_list.append('      MGSには存在しない ' + jav.title)
                    p_number = p_tool.get_p_number(jav.title)
                    site_data = fanza.get_info(p_number)
                    if site_data is None:
                        err_list.append('    FANZAにも存在しない')
                        continue
                    # site_data.print('FANZA ')
                    site_name = 'FANZA'
                    site_data.productNumber = jav.productNumber
                try:
                    new_maker = parser.get_maker_from_site(site_data, site_name)
                    if new_maker is not None:
                        err_list.append('   ' + new_maker.get_print_list('    ')[0])
                        p_tool.append_maker(new_maker)
                except common.MatchStrSameError as err:
                    print(str(err))
                except common.MatchStrNotFoundError as err:
                    print(jav.title)
                    print(str(err))

        if ng_reason == -22:
            p_number = p_tool.get_p_number(jav.title)
            site_data = fanza.get_info(p_number)
            if site_data is None:
                err_list.append('    FANZAには存在しない')
            else:
                err_list.append('    FANZA 【' + site_data.streamDate + '】')
                # if not is_checked:
                # jav_dao.update_maker_label(site_data.maker, site_data.label, jav.id)

        if len(jav.productNumber) <= 0:
            err_list.append('  add p_number [' + p_number + ']')

        if ng_reason == -21 or ng_reason == -22 or ng_reason == -23:
            if p_number != jav.productNumber:
                err_list.append('  p_number change [' + p_number + '] <-- [' + jav.productNumber + ']')
                if not is_checked:
                    jav_dao.update_product_number(jav.id, p_number)

        if new_maker is not None:
            new_maker.print('NEW ')
            if not is_checked:
                maker_dao.export(new_maker)

for err in err_list:
    print(err)

print('ok [' + str(ok_cnt) + ']')
print('ng [' + str(ng_cnt) + ']')
