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
              '  , makers_id, search_result ' \
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
            jav.searchResult = row[18]
            jav.createdAt = row[19]
            jav.updatedAt = row[20]
            javs.append(jav)

        return javs

    def is_exist(self, title: str) -> bool:

        if title is None or len(title) <= 0:
            return False

        sql = 'SELECT title ' \
              '  FROM jav WHERE title = %s '

        self.cursor.execute(sql, (title, ))

        rs = self.cursor.fetchall()
        exist = False

        if rs is not None:
            for row in rs:
                exist = True
                break

        return exist

    def update_collect_info(self, jav_data: data.JavData):

        sql = 'UPDATE jav ' \
              '  SET package = %s ' \
              '    , thumbnail = %s ' \
              '    , download_links = %s ' \
              '  WHERE id = %s'

        self.cursor.execute(sql, (jav_data.package, jav_data.thumbnail, jav_data.downloadLinks, jav_data.id))
        print("jav update id [" + str(id) + "] collect_info")

        self.conn.commit()

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

    def update_package(self, id, package_filename):

        sql = 'UPDATE jav ' \
                '  SET package = %s ' \
                '  WHERE id = %s'

        self.cursor.execute(sql, (package_filename, id))
        print("jav update id [" + str(id) + "]")

        self.conn.commit()

    def update_site_info(self, label, sell_date, id):

        sql = 'UPDATE jav ' \
              '  SET label = %s, sell_date = %s, is_site = 1 ' \
              '  WHERE id = %s'

        self.cursor.execute(sql, (label, sell_date, id))
        print("jav update id [" + str(id) + "] site_info")

        self.conn.commit()

    def update_search_result(self, search_result: str = '', id: int = 0):

        sql = 'UPDATE jav ' \
              '  SET search_result = %s ' \
              '  WHERE id = %s'

        self.cursor.execute(sql, (search_result, id))
        print("jav update id [" + str(id) + "] search_result")

        self.conn.commit()

    def export(self, jav_data: data.JavData):

        sql = 'INSERT INTO jav (title, post_date ' \
                '  , sell_date, actress, maker, label' \
                '  , url, product_number, makers_id, is_parse2 ' \
                '  ) ' \
                ' VALUES(%s, %s' \
                '  , %s, %s, %s, %s' \
                '  , %s, %s, %s, %s' \
                ' )'

        self.cursor.execute(sql, (jav_data.title, jav_data.postDate
                            , jav_data.sellDate, jav_data.actress, jav_data.maker, jav_data.label
                            , jav_data.url, jav_data.productNumber, jav_data.makersId, jav_data.isParse2
                            ))

        self.conn.commit()
