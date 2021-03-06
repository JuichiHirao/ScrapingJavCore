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

    def get_where_agreement(self, where: str = '', param_list: list = None):

        sql = self.__get_sql_select(where)

        if param_list:
            self.cursor.execute(sql, param_list)
        else:
            self.cursor.execute(sql)

        rs = self.cursor.fetchall()

        makers = self.__get_list(rs)

        if makers is None or len(makers) <= 0:
            return None

        return makers

    def __get_sql_select(self, where: str = ''):

        sql = 'SELECT id ' \
              '  , name, match_name, label, match_label ' \
              '  , kind, match_str, match_product_number, site_kind ' \
              '  , replace_words, p_number_gen, registered_by ' \
              '  , created_at, updated_at ' \
              '  FROM maker '

        if len(where) > 0:
            sql = sql + where + ' ORDER BY id '
        else:
            sql = sql + 'WHERE deleted = 0 ORDER BY id '

        return sql

    def __get_list(self, rs):

        makers = []
        for row in rs:
            maker = data.MakerData()
            maker.id = row[0]
            maker.name = row[1]
            maker.matchName = row[2]
            maker.label = row[3]
            maker.matchLabel = row[4]
            maker.kind = row[5]
            maker.matchStr = row[6]
            maker.matchProductNumber = row[7]
            maker.siteKind = row[8]
            maker.replaceWords = row[9]
            maker.pNumberGen = row[10]
            maker.registeredBy = row[11]
            maker.createdAt = row[12]
            maker.updatedAt = row[13]
            makers.append(maker)

        return makers

    def get_exist(self, match_str: str = ''):

        makers = self.get_where_agreement('WHERE match_str = %s and deleted = 0', (match_str, ))

        if makers is None or len(makers) <= 0:
            return None

        return makers[0]

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

    def update_deleted(self, deleted: str = '', id: int = 0):

        sql = 'UPDATE maker ' \
              '  SET deleted = %s ' \
              '  WHERE id = %s'

        self.cursor.execute(sql, (deleted, id))
        print("maker update id [" + str(id) + "] deleted ")

        return

    def export(self, maker):

        sql = 'INSERT INTO maker ( ' \
              '  name, match_name, label, match_label, kind ' \
              '  , match_str, match_product_number, site_kind, replace_words ' \
              '  , p_number_gen, registered_by ' \
              '  ) ' \
              '  VALUES ( ' \
              '  %s, %s, %s, %s, %s ' \
              '  , %s, %s, %s, %s ' \
              '  , %s, %s ' \
              '  ) '

        self.cursor.execute(sql, (maker.name, maker.matchName, maker.label, maker.matchLabel, maker.kind
                                  , maker.matchStr, maker.matchProductNumber, maker.siteKind, maker.replaceWords
                                  , maker.pNumberGen, maker.registeredBy
                                  ))

        self.conn.commit()

