from . import mysql_base
from .. import data


class MakerDao(mysql_base.MysqlBase):

    def get_all(self):

        sql = self.__get_sql_select()

        self.cursor.execute(sql)

        rs = self.cursor.fetchall()

        makers = self.__get_list(rs)

        if makers is None or len(makers) <= 0:
            return None

        return makers

    def __get_sql_select(self):

        sql = 'SELECT id ' \
              '  , name, match_name, label, kind ' \
              '  , match_str, match_product_number, site_kind, replace_words ' \
              '  , p_number_gen, registered_by ' \
              '  , created_at, updated_at ' \
              '  , created_at, updated_at ' \
              '  FROM maker ' \
              '  WHERE deleted = 0 ' \
              '  ORDER BY id'

        return sql

    def __get_list(self, rs):

        makers = []
        for row in rs:
            maker = data.MakerData()
            maker.id = row[0]
            maker.name = row[1]
            maker.matchName = row[2]
            maker.label = row[3]
            maker.kind = row[4]
            maker.matchStr = row[5]
            maker.matchProductNumber = row[6]
            maker.siteKind = row[7]
            maker.replaceWords = row[8]
            maker.pNumberGen = row[9]
            maker.registeredBy = row[10]
            maker.createdAt = row[11]
            maker.updatedAt = row[12]
            makers.append(maker)

        return makers

    def is_exist(self, match_str: str) -> bool:

        if match_str is None or len(match_str) <= 0:
            return False

        sql = 'SELECT id  FROM maker WHERE match_str = %s and deleted = 0 '

        self.cursor.execute(sql, (match_str, ))

        rs = self.cursor.fetchall()
        exist = False

        if rs is not None:
            for row in rs:
                exist = True
                break

        return exist

    def export(self, maker: data.MakerData):

        sql = 'INSERT INTO maker ( ' \
              '  name, match_name, label, kind ' \
              '  , match_str, match_product_number, site_kind, replace_words ' \
              '  , p_number_gen, registered_by ' \
              '  ) ' \
              '  VALUES ( ' \
              '  %s, %s, %s, %s ' \
              '  , %s, %s, %s, %s ' \
              '  , %s, %s ' \
              '  ) '

        self.cursor.execute(sql, (maker.name, maker.matchName, maker.label, maker.kind
                                  , maker.matchStr, maker.matchProductNumber, maker.siteKind, maker.replaceWords
                                  , maker.pNumberGen, maker.registeredBy
                                  ))

        self.conn.commit()

