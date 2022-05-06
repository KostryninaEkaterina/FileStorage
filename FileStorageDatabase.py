import sqlite3
from typing import List, Dict, Any
import copy


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
        insert = 'INSERT OR IGNORE INTO ' + self._db_name\
                 + '(id, name, tag, size, mimeType, modificationTime) VALUES(?,?,?,?,?,?)'
        self.cursor.execute(
            insert,
            valuesList
        )
        self.connection.commit()

    def loading_by_id(self, id: str):
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

    def loading_by_params(self, params: dict) -> dict:
        self._make_table()
        request = 'SELECT * FROM ' + self._db_name + self._get_where_string(params) + ' ORDER BY id'
        self.cursor.execute(request)
        result = self.cursor.fetchall()
        return self._create_list_of_dict(result)

    def loading_all(self) -> List[Dict[str, Any]]:
        self._make_table()
        request = 'SELECT * FROM ' + self._db_name + ' ORDER BY id'
        self.cursor.execute(request)
        result = self.cursor.fetchall()
        return self._create_list_of_dict(result)

    def delete(self, params) -> int:
        self._make_table()
        list_data = self.loading_by_params(params)
        request = 'DELETE from ' + self._db_name + self._get_where_string(params) #форматирование строк
        self.cursor.execute(request)
        self.connection.commit()
        return len(list_data)

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
            list_of_dict.append(copy.copy(table_dict))
        return list_of_dict

    def _get_where_string(self, data: dict) -> str:
        request_list = []
        for key, v in data.items():
            values = ", ".join("'" + elem + "'" for elem in v)
            request = key + ' IN(' + values + ')'
            request_list.append(request)
        where_str = ' WHERE ' + ' AND '.join(request_list)
        return where_str

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
