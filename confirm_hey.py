from src import site
from src import tool
from src import db

jav_dao = db.jav.JavDao()

javs = jav_dao.get_where_agreement('WHERE id = 14081') # 4004_343
hey = site.hey.Hey()
p_tool = tool.p_number.ProductNumber()
p_number, seller, sell_date, match_maker, ng_reason = p_tool.parse_and_fc2(javs[0], True)
site_data = hey.get_info(p_number)
site_data.print()
