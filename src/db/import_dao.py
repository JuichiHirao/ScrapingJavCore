from . import mysql_base
from .. import data


class ImportDao(mysql_base.MysqlBase):

    def update_p_number_info(self, id, product_number, match_maker):

        sql = 'UPDATE import ' \
              '  SET kind = %s ' \
              '   , match_product = %s ' \
              '   , product_number = %s ' \
              '   , maker = %s ' \
              '  WHERE id = %s '

        self.cursor.execute(sql, (match_maker.kind, match_maker.matchProductNumber, product_number, match_maker.get_maker(''), id))

    def export_import(self, importData: data.ImportData):

        sql = 'INSERT INTO import(copy_text, jav_post_date ' \
                ', kind, match_product, product_number, sell_date ' \
                ', maker, title, actresses, rar_flag ' \
                ', tag, filename, hd_kind, movie_file_id' \
                ', split_flag, name_only_flag, package, thumbnail ' \
                ', download_files, jav_url, rating, size) ' \
                ' VALUES(%s, %s' \
                ', %s, %s, %s, %s' \
                ', %s, %s, %s, %s' \
                ', %s, %s, %s, %s' \
                ', %s, %s, %s, %s' \
                ', %s, %s, %s, %s)'

        self.cursor.execute(sql, (importData.copy_text, importData.postDate
                            , importData.kind, importData.matchStr, importData.productNumber, importData.sellDate
                            , importData.maker, importData.title, importData.actress, importData.isRar
                            , importData.tag, importData.filename, importData.hd_kind, 0
                            , importData.isSplit, importData.isNameOnly, importData.package, importData.thumbnail
                            , importData.downloadFiles, importData.url, importData.rating, importData.size))

        self.conn.commit()

        return
