from . import mysql_base
from .. import data


class BackupHistoryDao(mysql_base.MysqlBase):

    def __init__(self):
        super().__init__(dbname='backup')

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
        sql = 'SELECT id, jav_id' \
              '  , title, post_date, package, thumbnail ' \
              '  , sell_date, actress, maker, label ' \
              '  , download_links, download_files, url, is_selection ' \
              '  , product_number, rating, is_site, is_parse2 ' \
              '  , makers_id, search_result, detail, files_info ' \
              '  , created_at, updated_at ' \
              '  FROM jav_history '

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
            jav.detail = row[19]
            jav.filesInfo = row[20]
            jav.createdAt = row[21]
            jav.updatedAt = row[22]
            javs.append(jav)

        return javs

    def is_exist_by_id(self, id: int, table_name: str) -> bool:

        if table_name is None or len(table_name) <= 0:
            print('table[{}]が存在しない'.format(table_name))
            return False

        if table_name == 'jav_history':
            column_name = 'jav_id'
        else:
            column_name = 'jav2_id'

        sql = 'SELECT {} FROM backup.{} WHERE {} = %s '.format(column_name, table_name, column_name)

        self.cursor.execute(sql, (id, ))

        rs = self.cursor.fetchall()
        exist = False

        if rs is not None:
            for row in rs:
                exist = True
                break

        return exist

    def export_jav(self, jav_data: data.JavData):

        sql = 'INSERT INTO backup.jav_history (jav_id ' \
                '  , title, `name`, post_date, package ' \
                '  , thumbnail, sell_date, actress, maker ' \
                '  , label, download_links, download_files, files_info ' \
                '  , url, product_number, is_selection, rating' \
                '  , is_parse2, is_site, makers_id, search_result ' \
                '  , detail, created_at_original, updated_at_original ' \
                '  ) ' \
                ' VALUES(%s' \
                '  , %s, %s, %s, %s' \
                '  , %s, %s, %s, %s' \
                '  , %s, %s, %s, %s' \
                '  , %s, %s, %s, %s' \
                '  , %s, %s, %s, %s' \
                '  , %s, %s, %s ' \
                ' )'

        self.cursor.execute(sql, (jav_data.id
                                  , jav_data.title, jav_data.name, jav_data.postDate, jav_data.package
                                  , jav_data.thumbnail, jav_data.sellDate, jav_data.actress, jav_data.maker
                                  , jav_data.label, jav_data.downloadLinks, jav_data.downloadFiles, jav_data.filesInfo
                                  , jav_data.url, jav_data.productNumber, jav_data.isSelection, jav_data.rating
                                  , jav_data.isParse2, jav_data.isSite, jav_data.makersId, jav_data.searchResult
                                  , jav_data.detail, jav_data.createdAt, jav_data.updatedAt)
                            )

        self.conn.commit()

    def export_jav2(self, jav2_data: data.Jav2Data):
        sql = 'INSERT INTO backup.jav2_history (jav2_id ' \
              '  , title, post_date, package, thumbnail ' \
              '  , download_links, files_info, kind, url ' \
              '  , detail, created_at_original, updated_at_original ' \
              '  ) ' \
              ' VALUES(%s' \
              '  , %s, %s, %s, %s' \
              '  , %s, %s, %s, %s' \
              '  , %s, %s, %s ' \
              ' )'

        self.cursor.execute(sql, (jav2_data.id
                                  , jav2_data.title, jav2_data.postDate, jav2_data.package, jav2_data.thumbnail
                                  , jav2_data.downloadLinks, jav2_data.filesInfo, jav2_data.kind, jav2_data.url
                                  , jav2_data.detail, jav2_data.createdAt, jav2_data.updatedAt)
                            )

        self.conn.commit()

