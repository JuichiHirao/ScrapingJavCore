from . import mysql_base
from .. import data


class Jav2Dao(mysql_base.MysqlBase):

    def get_where_agreement(self, where):

        sql = self.__get_sql_select()
        sql = sql + where

        self.cursor.execute(sql)

        rs = self.cursor.fetchall()

        javs = self.__get_list(rs)

        if javs is None or len(javs) <= 0:
            return None

        return javs

    def get_where_agreement_param(self, where, params):

        sql = self.__get_sql_select()
        sql = sql + where

        self.cursor.execute(sql, params)

        # rowcountは戻りがあっても、正しい件数を取得出来ない
        # rowcount = self.cursor.rowcount
        rs = self.cursor.fetchall()

        jav2s = self.__get_list(rs)

        self.conn.commit()

        return jav2s

    def __get_sql_select(self):
        sql = 'SELECT id ' \
              '  , title, download_links, kind, url ' \
              '  , detail ' \
              '  , created_at, updated_at ' \
              '  FROM jav2 '

        return sql

    def __get_list(self, rs):

        javs = []
        for row in rs:
            jav = data.Jav2Data()
            jav.id = row[0]
            jav.title = row[1]
            jav.downloadLinks = row[2]
            jav.kind = row[3]
            jav.url = row[4]
            jav.detail = row[5]
            jav.createdAt = row[6]
            jav.updatedAt = row[7]
            javs.append(jav)

        return javs
