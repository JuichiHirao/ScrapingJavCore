import re
from .. import data


class CopyText:

    def __init__(self, is_debug: bool = False):
        self.is_debug = is_debug

    def get_title(self, copy_text: str = '', product_number: str = '', match_maker: data.MakerData = None):

        hankaku = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', ' ']
        zenkaku = ['１', '２', '３', '４', '５', '６', '７', '８', '９', '０', '　']
        movie_kind = ''

        if match_maker:
            if match_maker.replaceWords is not None and len(match_maker.replaceWords) > 0:
                words = match_maker.replaceWords.split(' ')
                for word in words:
                    copy_text = re.sub(word, '', copy_text)

        # re_movie = re.compile(self.movie_extension, re.IGNORECASE)

        match_search = re.search('[\[]*FHD[\]]*', copy_text)
        if match_search:
            title = copy_text.replace(match_search.group(), '').replace(product_number.upper(), '', ) \
                .replace(product_number.lower(), '', )
            movie_kind = ' FHD'
        else:
            # print('p_num [', str(product_number) + ']')
            title = copy_text.replace(product_number, '').strip()

        if len(movie_kind) > 0:
            title = title.strip() + movie_kind

        if match_maker:
            match_maker_name = re.search(match_maker.matchName, title)
            if match_maker_name:
                title = title.replace(match_maker_name.group(), '')

            match_maker_str = re.search(match_maker.matchStr, title)
            if match_maker_str:
                title = title.replace(match_maker_str.group(), '')

        edit_copytext = title
        for idx, char in enumerate(zenkaku):
            m = re.search(char, edit_copytext)
            if m:
                edit_copytext = edit_copytext.replace(char, hankaku[idx])

        title = edit_copytext

        if self.is_debug:
            print('  before [' + copy_text + ']')
            print('  after  [' + title.strip() + ']')

        return title.strip()
