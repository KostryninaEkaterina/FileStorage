import sqlite3


class DataStorage:
    _db_name: str = str()

    def __init__(self, db_name: str = 'FileDatabase'):
        self._db_name = db_name
        self.connection = sqlite3.connect('File.txt')
        self.cursor = self.connection.cursor()

    def _make_table(self):
        cr_table = 'CREATE TABLE IF NOT EXISTS ' + self._db_name + \
                   '(id TEXT, name TEXT, tag TEXT,size REAL, mimeType TEXT, modificationTime TEXT,  UNIQUE(id))'
        self.cursor.execute(cr_table)
        self.connection.commit()

    def save_in_table(self, data: dict) -> None:
        self._make_table()
        valuesList = []
        for key in data:
            valuesList.append(data[key])
        valuesList = tuple(valuesList)
        print(valuesList)
        # data_tuple = tuple(valuesList)
        # print(data_tuple)
        insert = 'INSERT OR IGNORE INTO ' + self._db_name + '(id, name, tag, size, mimeType, modificationTime) VALUES(?,?,?,?,?,?)'
        # for data_dict in data:    data: list[dict] или data: dict ?...

        self.cursor.execute(
            insert,
            valuesList
        )
        self.connection.commit()

    def loading_by_id(self, id: str) -> dict:
        self._make_table()
        request = 'SELECT * FROM ' + self._db_name + ' WHERE id =' + id
        self.cursor.execute(request)
        result = self.cursor.fetchall()
        return self._create_list_of_dict(result)

    def get_name_by_id(self, id:str):
        self._make_table()
        request = 'SELECT name FROM ' + self._db_name + ' WHERE id =' + id
        self.cursor.execute(request)
        result = self.cursor.fetchall()
        return result

    def loading_by_name(self, name: str) -> dict:
        self._make_table()
        request = 'SELECT * FROM ' + self._db_name + ' WHERE name =' + name
        self.cursor.execute(request)
        result = self.cursor.fetchall()
        print(result)
        table_dict = {}
        for elem in result:
            k, v = elem[0], elem[1]
            table_dict[k] = v
        return table_dict

    def loading_all(self) -> dict:
        self._make_table()
        request = 'SELECT * FROM ' + self._db_name
        self.cursor.execute(request)
        result = self.cursor.fetchall()
        return self._create_list_of_dict(result)


    def delete(self, id: str):
        self._make_table()
        request = 'DELETE from ' + self._db_name + ' WHERE id = ' + id  # форматирование строк
        self.cursor.execute(request)
        self.connection.commit()

    def _create_list_of_dict(self, result_list: list):
        list_of_dict = []
        table_dict = {}
        for elem in result_list:
            table_dict['id'] = elem[0]
            table_dict['name'] = elem[1]
            table_dict['tag'] = elem[2]
            table_dict['size'] = elem[3]
            table_dict['mimeType'] = elem[4]
            table_dict['modificationTime'] = elem[5]
            list_of_dict.append(table_dict)
        return list_of_dict

    def update(self, data: dict):
        self._make_table()
        sql_update_query = """
        UPDATE FileDatabase
        SET name = ?, tag = ?, size = ?, mimeType = ?, modificationTime = ?
        WHERE id = ?"""
        params = (data['name'],
                  data['tag'],
                  data['size'],
                  data['mimeType'],
                  data['modificationTime'],
                  data['id'])
        self.cursor.execute(sql_update_query, params)
        self.connection.commit()
