from . import mysql_base
from .. import data


class ReplaceInfoDao(mysql_base.MysqlBase):

    def get_all(self):

        sql = self.__get_sql_select()

        self.cursor.execute(sql)

        rs = self.cursor.fetchall()

        rep_info_list = self.__get_list(rs)

        if rep_info_list is None or len(rep_info_list) <= 0:
            return None

        return rep_info_list

    def get_where_agreement(self, where):

        sql = self.__get_sql_select()
        sql = sql + where

        self.cursor.execute(sql)

        rs = self.cursor.fetchall()

        rep_info_list = self.__get_list(rs)

        if rep_info_list is None or len(rep_info_list) <= 0:
            return None

        return rep_info_list

    def __get_sql_select(self):
        sql = 'SELECT id' \
              '  , type, source, destination, source_type ' \
              '  , created_at, updated_at ' \
              '  FROM replace_info '

        return sql

    def __get_list(self, rs):

        replace_info_list = []
        for row in rs:
            replace_info = data.ReplaceInfoData()
            replace_info.id = row[0]
            replace_info.type = row[1]
            replace_info.source = row[2]
            replace_info.destination = row[3]
            replace_info.sourceType = row[4]
            replace_info.createdAt = row[5]
            replace_info.updatedAt = row[6]
            replace_info_list.append(replace_info)

        return replace_info_list

    def update(self, replace_info: data.ReplaceInfoData):

        sql = 'UPDATE replace_info ' \
              '  SET type = %s, source = %s, destination = %s, source_type = %s ' \
              '  WHERE id = %s'

        self.cursor.execute(sql, (replace_info.type, replace_info.source, replace_info.destination
                                  , replace_info.sourceType, replace_info.id))
        print("replace_info update id [" + str(id) + "] all")

        self.conn.commit()

    def export(self, replace_info: data.ReplaceInfoData):

        sql = 'INSERT INTO replace_info ( ' \
              '  type, source, destination, source_type' \
              '  ) ' \
              ' VALUES(' \
              '  %s, %s, %s, %s' \
              ' )'

        self.cursor.execute(sql, (replace_info.type, replace_info.source
                                  , replace_info.destination, replace_info.sourceType
                                  ))

        self.conn.commit()
