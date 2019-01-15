from src import site
from src import tool
from src import db
from src import common

jav_dao = db.jav.JavDao()

# fc2 = site.fc2.Fc2()
mgs = site.mgs.Mgs()
javs = jav_dao.get_where_agreement('WHERE is_parse2 <= 0 and is_selection = 1')

parser = common.AutoMakerParser()

print('target [' + str(len(javs)) + ']')
p_tool = tool.p_number.ProductNumber(is_log_print=False)
err_list = []
ok_cnt = 0
ng_cnt = 0
is_checked = True
for jav in javs:

    match_maker, ng_reason = p_tool.parse(jav, is_checked)

    if ng_reason > 0:
        # match_maker.print()
        p_tool.get_log_print()
        ok_cnt = ok_cnt + 1
    else:
        err_list.append(str(jav.id) + ' [' + str(ng_reason) + '] ' + jav.title)
        err_list.append('    ' + str(p_tool.get_log_print()))
        ng_cnt = ng_cnt + 1
        # -1 : メーカー名に一致するmaker無し
        # -3 : メーカー一致が複数件、match_strに一致するmaker無し
        #   メーカーに登録
        if ng_reason == -1 or ng_reason == -3:
            try:
                new_maker = parser.get_maker(jav)
                new_maker.print()
                p_tool.append_maker(new_maker)
            except common.MatchStrSameError as err:
                print(str(err))
        #   -2 : メーカー名1件だけ完全一致したが、match_strの文字列がtitleにない
        #   -21 : タイトル内にpNumberは存在したが、一致するメーカーは存在しない
        if ng_reason == -21:
            hey_p_number, hey_label = p_tool.get_p_number_hey(jav.title)

            if len(hey_p_number) > 0:
                err_list.append('      【' + hey_p_number + '】 ' + hey_label)
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

    '''
    print('p_number ' + jav.productNumber)
    if jav.isParse2 == -3 or jav.isParse2 == -4:
        continue

    p_number, seller, sell_date, match_maker, ng_reason = p_tool.parse_and_fc2(jav, True)

    print('seller_date ' + str(sell_date) + '  seller ' + seller)
    if ng_reason < 0:
        if mgs.exist_product_number(jav.productNumber):
            site_data = mgs.get_info(jav.productNumber)
            if site_data is not None:
                continue
        err_list.append(str(jav.id) + ' failed [' + str(ng_reason) + ']  ' + jav.title)
    '''

for err in err_list:
    print(err)

print('ok [' + str(ok_cnt) + ']')
print('ng [' + str(ng_cnt) + ']')
