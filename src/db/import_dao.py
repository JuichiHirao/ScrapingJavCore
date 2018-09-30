from . import mysql_base
from .. import data


class ImportDao(mysql_base.MysqlBase):

    def export_import(self, importData: data.ImportData):

        sql = 'INSERT INTO import(copy_text, jav_post_date ' \
                ', kind, match_product, product_number, sell_date ' \
                ', maker, title, actresses, rar_flag ' \
                ', tag, filename, hd_kind, movie_file_id' \
                ', split_flag, name_only_flag, jav_url, rating ' \
                ', size) ' \
                ' VALUES(%s, %s' \
                ', %s, %s, %s, %s' \
                ', %s, %s, %s, %s' \
                ', %s, %s, %s, %s' \
                ', %s, %s, %s, %s' \
                ', %s)'

        self.cursor.execute(sql, (importData.copy_text, importData.postDate
                            , importData.kind, importData.matchStr, importData.productNumber, importData.sellDate
                            , importData.maker, importData.title, importData.actress, importData.isRar
                            , importData.tag, importData.filename, importData.hd_kind, 0
                            , importData.isSplit, importData.isNameOnly, importData.url, importData.rating
                            , importData.size))

        self.conn.commit()

        return
