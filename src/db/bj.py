from . import mysql_base
from .. import data


class BjDao(mysql_base.MysqlBase):

    def get_all(self):

        sql = self.__get_sql_select()
        sql = sql + " ORDER BY post_date "

        self.cursor.execute(sql)

        rs = self.cursor.fetchall()

        bjs = self.__get_list(rs)

        if bjs is None or len(bjs) <= 0:
            return None

        return bjs

    def get_where_agreement(self, where):

        sql = self.__get_sql_select()
        sql = sql + where

        self.cursor.execute(sql)

        rs = self.cursor.fetchall()

        bjs = self.__get_list(rs)

        if bjs is None or len(bjs) <= 0:
            return None

        return bjs

    def __get_sql_select(self):

        sql = 'SELECT id' \
              '  , title, post_date, thumbnails, thumbnails_count ' \
              '  , download_link, url, posted_in, is_selection ' \
              '  , is_downloads, rating ' \
              '  , created_at, updated_at ' \
              '  FROM bj '

        return sql

    def __get_list(self, rs):

        bjs = []
        for row in rs:
            bj = data.BjData()
            bj.id = row[0]
            bj.title = row[1]
            bj.postDate = row[2]
            bj.thumbnails = row[3]
            bj.thumbnailsCount = row[4]
            bj.downloadLink = row[5]
            bj.url = row[6]
            bj.postedIn = row[7]
            bj.isSelection = row[8]
            bj.isDownloads = row[9]
            bj.rating = row[10]
            bj.createdAt = row[11]
            bj.updatedAt = row[12]
            bjs.append(bj)

        return bjs

    def is_exist(self, title: str) -> bool:

        if title is None or len(title) <= 0:
            return False

        sql = 'SELECT title ' \
              '  FROM bj WHERE title = %s '

        self.cursor.execute(sql, (title, ))

        rs = self.cursor.fetchall()
        exist = False

        if rs is not None:
            for row in rs:
                exist = True
                break

        return exist

    def update_is_download(self, id, is_downloads):

        sql = 'UPDATE bj ' \
              '  SET is_downloads = %s ' \
              '  WHERE id = %s'

        self.cursor.execute(sql, (is_downloads, id))
        print("bj update id [" + str(id) + "] is_downloads")

        self.conn.commit()

    def update_is_selection(self, id, is_selection):

        sql = 'UPDATE bj ' \
              '  SET is_selection = %s ' \
              '  WHERE id = %s'

        self.cursor.execute(sql, (is_selection, id))
        print("bj update id [" + str(id) + "] is_selection")

        self.conn.commit()

    def export(self, import_data: data.ImportData):

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

        self.cursor.execute(sql, (import_data.copy_text, import_data.postDate
                                  , import_data.kind, import_data.matchStr, import_data.productNumber, import_data.sellDate
                                  , import_data.maker, import_data.title, import_data.actress, import_data.isRar
                                  , import_data.tag, import_data.filename, import_data.hd_kind, 0
                                  , import_data.isSplit, import_data.isNameOnly, import_data.url, import_data.rating
                                  , import_data.size))

        self.conn.commit()

    def export(self, bj_data):

        sql = 'INSERT INTO bj(title, post_date ' \
                ', thumbnails, thumbnails_count, download_link, url, posted_in) ' \
                ' VALUES(%s, %s, %s, %s, %s, %s, %s)'

        self.cursor.execute(sql, (bj_data.title, bj_data.postDate
                            , bj_data.thumbnails, bj_data.thumbnailsCount
                            , bj_data.downloadLink, bj_data.url
                            , bj_data.postedIn))

        self.conn.commit()

