from src import site

mgs = site.mgs.Mgs()
# detail, sell_date = mgs.get_info('277DCV-093')
detail, sell_date = mgs.test_execute()
# print(' [' + str(sell_date) + '] ' + detail)

