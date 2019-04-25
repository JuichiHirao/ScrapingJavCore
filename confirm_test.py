import re
from src import common
from src import data

'''
match_maker = data.MakerData()
match_maker.matchName = 'S1 NO.1 STYLE'
match_maker.matchStr = 'SSNI'
match_maker.matchProductNumber = ''
copy_text = common.CopyText()
# title = copy_text.get_title('[FHD6m]ssni-391 隣に住む引きこもりの幼馴染に私、毎日アニコスを着させられて… 夢乃あいか', 'SSNI-391')
title = copy_text.get_title('[FHD]ssni-391 隣に住む引きこもりの幼馴染に私、毎日アニコスを着させられて… 夢乃あいか', 'SSNI-391')
print(title)
'''

env = common.Environment()

# print(' [' + env.get_exist_image_path('102044785_0016cbb5.jpg') + ']')
print(' [' + env.get_exist_image_path('4785_0016cbb5.jpg') + ']')
