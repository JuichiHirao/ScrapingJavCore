import re
from src import site
from src import tool
from src import db
from src import common
from datetime import datetime

jav_dao = db.jav.JavDao()
maker_dao = db.maker.MakerDao()
makers = maker_dao.get_where_agreement('WHERE id = 835')

fc2 = site.fc2.Fc2()
javs = jav_dao.get_where_agreement('WHERE is_selection = 1 and makers_id = 835 and sell_date is null order by id')
# javs = jav_dao.get_where_agreement('WHERE id = 16891 order by id limit 50')

if javs is None:
    javs = []
print('target [' + str(len(javs)) + ']')
p_tool = tool.p_number.ProductNumber(is_log_print=False)
err_list = []
is_checked = False
fc2_maker = makers[0]

for jav in javs:

    if jav.makersId != 835:
        print('not fc2')
        continue

    # match_maker, ng_reason = p_tool.parse(jav, is_checked)

    m_p_number = re.search(fc2_maker.matchProductNumber, jav.title)
    if m_p_number:
        p_number = m_p_number.group()
        print(p_number + ' <-- ' + jav.productNumber)
        jav_dao.update_product_number(jav.id, p_number)
        site_data = fc2.get_info(p_number)
        if site_data is not None:
            print(site_data.streamDate+ ' ' + site_data.maker)
            jav_dao.update_site_info(site_data.maker, site_data.streamDate, jav.id)
        else:
            print('site_data is none ' + jav.title)
    else:
        print('p_number not found')
