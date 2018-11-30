from . import mysql_base
from .. import data


class ImportDao(mysql_base.MysqlBase):

    def get_all(self):

        sql = self.__get_sql_select()
        sql = sql + " ORDER BY id "

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

        imports = self.__get_list(rs)

        if imports is None or len(imports) <= 0:
            return None

        return imports

    def __get_sql_select(self):

        sql = 'SELECT id' \
              '  , copy_text, kind, match_product, product_number' \
              '  , sell_date, maker, title, actresses ' \
              '  , rar_flag, tag, filename, hd_kind ' \
              '  , movie_file_id, split_flag, name_only_flag, jav_post_date ' \
              '  , package, thumbnail, download_files, search_result ' \
              '  , detail, jav_url, rating, `size` ' \
              '  , created_at, updated_at ' \
              '  FROM import '

        return sql

    def __get_list(self, rs):

        import_list = []

        for row in rs:
            import_data  = data.ImportData()
            import_data.id = row[0]
            import_data.copy_text = row[1]
            import_data.kind = row[2]
            import_data.matchStr = row[3]
            import_data.productNumber = row[4]
            import_data.sellDate = row[5]
            import_data.maker = row[6]
            import_data.title = row[7]
            import_data.actress = row[8]
            import_data.isRar = row[9]
            import_data.tag = row[10]
            import_data.filename = row[11]
            import_data.hd_kind = row[12]
            import_data.movieFileId = row[13]
            import_data.isSplit = row[14]
            import_data.isNameOnly = row[15]
            import_data.postDate = row[16]
            import_data.package = row[17]
            import_data.thumbnail = row[18]
            import_data.downloadFiles = row[19]
            import_data.searchResult = row[20]
            import_data.detail = row[21]
            import_data.url = row[22]
            import_data.rating = row[23]
            import_data.size = row[24]
            import_data.createdAt = row[25]
            import_data.updatedAt = row[26]
            import_list.append(import_data)

        return import_list

    def export_import(self, import_data: data.ImportData):

        sql = 'INSERT INTO import(copy_text, jav_post_date ' \
                ', kind, match_product, product_number, sell_date ' \
                ', maker, title, actresses, rar_flag ' \
                ', tag, filename, hd_kind, movie_file_id' \
                ', split_flag, name_only_flag, package, thumbnail ' \
                ', download_files, jav_url, rating, size' \
                ', search_result) ' \
                ' VALUES(%s, %s' \
                ', %s, %s, %s, %s' \
                ', %s, %s, %s, %s' \
                ', %s, %s, %s, %s' \
                ', %s, %s, %s, %s' \
                ', %s, %s, %s, %s' \
                ', %s)'

        self.cursor.execute(sql, (import_data.copy_text, import_data.postDate
                            , import_data.kind, import_data.matchStr, import_data.productNumber, import_data.sellDate
                            , import_data.maker, import_data.title, import_data.actress, import_data.isRar
                            , import_data.tag, import_data.filename, import_data.hd_kind, 0
                            , import_data.isSplit, import_data.isNameOnly, import_data.package, import_data.thumbnail
                            , import_data.downloadFiles, import_data.url, import_data.rating, import_data.size
                            , import_data.searchResult))

        self.conn.commit()

        return

    def update_search_result(self, search_result: str = '', id: int = 0):

        sql = 'UPDATE import ' \
              '  SET search_result = %s ' \
              '  WHERE id = %s'

        self.cursor.execute(sql, (search_result, id))
        print("import update id [" + str(id) + "] search_result")

        self.conn.commit()

    def update_p_number_info(self, id, product_number, match_maker):

        sql = 'UPDATE import ' \
              '  SET kind = %s ' \
              '   , match_product = %s ' \
              '   , product_number = %s ' \
              '   , maker = %s ' \
              '  WHERE id = %s '

        self.cursor.execute(sql, (match_maker.kind, match_maker.matchProductNumber, product_number, match_maker.get_maker(''), id))
        print("import update id [" + str(id) + "] p_number_info")

        self.conn.commit()

