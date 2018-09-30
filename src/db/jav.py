from . import mysql_base
from .. import data


class JavDao(mysql_base.MysqlBase):

    def get_all(self):

        sql = self.__get_sql_select()
        sql = sql + " ORDER BY post_date "

        self.cursor.execute(sql)

        rs = self.cursor.fetchall()

        javs = self.__get_list(rs)

        if javs is None or len(javs) <= 0:
            return None

        return javs

    def get_where_agreement(self, where):

        sql = self.__get_sql_select()
        sql = sql + where

        self.cursor.execute(sql)

        rs = self.cursor.fetchall()

        javs = self.__get_list(rs)

        if javs is None or len(javs) <= 0:
            return None

        return javs

    def __get_sql_select(self):
        sql = 'SELECT id' \
              '  , title, post_date, package, thumbnail ' \
              '  , sell_date, actress, maker, label ' \
              '  , download_links, download_files, url, is_selection ' \
              '  , product_number, rating, is_site, is_parse2 ' \
              '  , makers_id ' \
              '  , created_at, updated_at ' \
              '  FROM jav '

        return sql

    def __get_list(self, rs):

        javs = []
        for row in rs:
            jav = data.JavData()
            jav.id = row[0]
            jav.title = row[1]
            jav.postDate = row[2]
            jav.package = row[3]
            jav.thumbnail = row[4]
            jav.sellDate = row[5]
            jav.actress = row[6]
            jav.maker = row[7]
            jav.label = row[8]
            jav.downloadLinks = row[9]
            jav.downloadFiles = row[10]
            jav.url = row[11]
            jav.isSelection = row[12]
            jav.productNumber = row[13]
            jav.rating = row[14]
            jav.isSite = row[15]
            jav.isParse2 = row[16]
            jav.makersId = row[17]
            jav.createdAt = row[18]
            jav.updatedAt = row[19]
            javs.append(jav)

        return javs

    def update_is_selection(self, id, is_selection):

        sql = 'UPDATE jav ' \
              '  SET is_selection = %s ' \
              '  WHERE id = %s'

        self.cursor.execute(sql, (is_selection, id))
        print("jav update id [" + str(id) + "] is_selection")

        self.conn.commit()

    def update_product_number(self, id, product_number):

        sql = 'UPDATE jav ' \
              '  SET product_number = %s ' \
              '  WHERE id = %s'

        self.cursor.execute(sql, (product_number, id))
        print("jav update id [" + str(id) + "] product_number")

        self.conn.commit()

    def update_checked_ok(self, is_parse2, makers_id, javData):

        sql = 'UPDATE jav ' \
              '  SET is_parse2 = %s ' \
              '    , scraping.jav.makers_id = %s ' \
              '  WHERE id = %s'

        self.cursor.execute(sql, (is_parse2, makers_id, javData.id))
        print("jav update id [" + str(javData.id) + "] checked_ok")

        self.conn.commit()
