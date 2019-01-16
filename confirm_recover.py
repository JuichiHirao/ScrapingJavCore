from src import site
from src import tool
from src import db
from src import common

jav_dao = db.jav.JavDao()
maker_dao = db.maker.MakerDao()

# fc2 = site.fc2.Fc2()
mgs = site.mgs.Mgs()
hey = site.hey.Hey()
javs = jav_dao.get_where_agreement('WHERE is_parse2 <= 0 and is_selection = 1')

parser = common.AutoMakerParser()

print('target [' + str(len(javs)) + ']')
p_tool = tool.p_number.ProductNumber(is_log_print=False)
err_list = []
ok_cnt = 0
ng_cnt = 0
is_checked = True
for jav in javs:

    if jav.id == 14651:
        print('abc')
    match_maker, ng_reason = p_tool.parse(jav, is_checked)

    if ng_reason > 0:
        # match_maker.print()
        p_tool.get_log_print()
        ok_cnt = ok_cnt + 1
    else:
        new_maker = None
        err_list.append(str(jav.id) + ' [' + str(ng_reason) + '] ' + jav.title)
        err_list.append('    ' + str(p_tool.get_log_print()))
        ng_cnt = ng_cnt + 1
        # -1 : メーカー名に一致するmaker無し
        # -3 : メーカー一致が複数件、match_strに一致するmaker無し
        #   メーカーに登録
        # -2 : メーカー名1件だけ完全一致したが、match_strの文字列がtitleにない
        #   完全一致をdelete:1にして、メーカーに登録
        if ng_reason == -1 or ng_reason == -2 or ng_reason == -3:
            if ng_reason == -2:
                # err_list.append('-2発生、1件一致の[' + jav.productNumber + ']deletedを1にする必要あり')

                # deleted : 1 に更新
                arr_match_str = jav.productNumber.split('-')
                makers = maker_dao.get_where_agreement('WHERE match_str = %s', (arr_match_str[0]))
                if makers is not None and len(makers) == 1:
                    maker_dao.update_deleted(1, makers[0])
                else:
                    err_list.append('-2発生、1件一致のmaker [' + jav.productNumber + '] 発見できず')
            try:
                new_maker = parser.get_maker(jav)
                new_maker.print()
                p_tool.append_maker(new_maker)
            except common.MatchStrSameError as err:
                print(str(err))

        #   -21 : タイトル内にpNumberは存在したが、一致するメーカーは存在しない
        if ng_reason == -21:
            hey_p_number, hey_label = p_tool.get_p_number_hey(jav.title)

            if len(hey_p_number) > 0:
                makers = maker_dao.get_where_agreement('WHERE label = %s', (hey_label, ))

                if makers is not None:
                    err_list.append('      【' + hey_label + '】はmakerに存在 maker_id [' + str(makers[0].id))
                    continue

                err_list.append('      [' + hey_p_number + '] 【' + hey_label + '】')
                site_data = hey.get_info(hey_p_number)
                if site_data is None or len(site_data.maker) <= 0:
                    err_list.append('      HEYには存在しない ' + jav.title)
                    continue
                err_list.append('      [' + site_data.streamDate + '] 【' + site_data.maker + '】')
            else:
                p_number = p_tool.get_maker_match_number(None, jav.title)
                site_data = mgs.get_info(p_number)

                if site_data is None or len(site_data.productNumber) <= 0:
                    err_list.append('      MGSには存在しない ' + jav.title)
                    continue
                try:
                    new_maker = parser.get_maker_from_site(site_data, 'MGS')
                    if new_maker is not None:
                        err_list.append('   ' + new_maker.get_print_list('    ')[0])
                        p_tool.append_maker(new_maker)
                except common.MatchStrSameError as err:
                    print(str(err))
                except common.MatchStrNotFoundError as err:
                    print(jav.title)
                    print(str(err))

        if new_maker is not None:
            if not is_checked:
                maker_dao.export(new_maker)

for err in err_list:
    print(err)

print('ok [' + str(ok_cnt) + ']')
print('ng [' + str(ng_cnt) + ']')
