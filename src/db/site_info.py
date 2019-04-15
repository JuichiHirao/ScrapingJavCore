from . import mysql_base
from .. import data


class SiteInfoDao(mysql_base.MysqlBase):

    def get_all(self):

        sql = self.__get_sql_select()

        self.cursor.execute(sql)

        rs = self.cursor.fetchall()

        site_info_list = self.__get_list(rs)

        if site_info_list is None or len(site_info_list) <= 0:
            return None

        return site_info_list

    def get_where_agreement(self, where):

        sql = self.__get_sql_select()
        sql = sql + where

        self.cursor.execute(sql)

        rs = self.cursor.fetchall()

        site_info_list = self.__get_list(rs)

        if site_info_list is None or len(site_info_list) <= 0:
            return None

        return site_info_list

    def __get_sql_select(self):
        sql = 'SELECT id ' \
              '  , name, match_name, target_number, name_order ' \
              '  , url ' \
              '  , created_at, updated_at ' \
              '  FROM site_info ' \
              '  ORDER BY name_order '

        return sql

    def __get_list(self, rs):

        site_info_list = []
        for row in rs:
            site_info = data.SiteInfoData()
            site_info.id = row[0]
            site_info.name = row[1]
            site_info.matchStr = row[2]
            site_info.targetNumber = row[3]
            site_info.nameOrder = row[4]
            site_info.url = row[5]
            site_info.createdAt = row[6]
            site_info.updatedAt = row[7]

            site_info_list.append(site_info)

        return site_info_list
