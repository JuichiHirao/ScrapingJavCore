from src import site
from src import tool
from src import db
from src import common

jav_dao = db.jav.JavDao()

javs = jav_dao.get_where_agreement('WHERE is_selection = 9 order by created_at desc limit 100')

parser = common.AutoMakerParser()

print('target [' + str(len(javs)) + ']')
p_tool = tool.p_number.ProductNumber()
err_list = []
for jav in javs:
    print('p_number ' + jav.productNumber)
    p_number, seller, sell_date, match_maker, ng_reason = p_tool.parse_and_fc2(jav, True)

    if match_maker is None:
        msg = 'no match makerId[' + str(jav.makersId) + ']'
        err_list.append(msg)
        print(msg)
        continue
    if jav.makersId != match_maker.id:
        msg = 'no match makerId[' + str(jav.makersId + ']  match_maker [' + str(match_maker.id))
        err_list.append(msg)
        print(msg)
    else:
        msg = 'same_maker'
        # err_list.append(msg)
        # print(msg)

for err in err_list:
    print(err)
