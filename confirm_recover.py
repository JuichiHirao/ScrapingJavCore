from src import site
from src import tool
from src import db
from src import common

jav_dao = db.jav.JavDao()

# fc2 = site.fc2.Fc2()
# mgs = site.mgs.Mgs()
javs = jav_dao.get_where_agreement('WHERE is_parse2 <= 0 and is_selection = 1')

parser = common.AutoMakerParser()

print('target [' + str(len(javs)) + ']')
p_tool = tool.p_number.ProductNumber(is_log_print=False)
err_list = []
ok_cnt = 0
ng_cnt = 0
for jav in javs:

    match_maker, ng_reason = p_tool.parse(jav, True)

    if ng_reason > 0:
        match_maker.print()
        ok_cnt = ok_cnt + 1
    else:
        err_list.append(str(jav.id) + ' [' + str(ng_reason) + '] ' + jav.title)
        err_list.append('    ' + str(p_tool.get_log_print()))
        ng_cnt = ng_cnt + 1

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
