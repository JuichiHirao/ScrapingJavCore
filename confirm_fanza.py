from src import site
from src import tool
from src import db

jav_dao = db.jav.JavDao()

javs = jav_dao.get_where_agreement('WHERE id = 15867') # MACB-001
fanza = site.fanza.Fanza()
p_tool = tool.p_number.ProductNumber()
# p_number, seller, sell_date, match_maker, ng_reason = p_tool.parse_and_fc2(javs[0], True)
site_data = fanza.get_info('SDMU-912')
# site_data.print()
