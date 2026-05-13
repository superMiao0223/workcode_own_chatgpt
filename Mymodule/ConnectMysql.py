import datetime

import pymysql
from retrying import retry

class ConnectMysql():
    def __init__(self,conncetdict = None):
        self.conncetdict = {} if conncetdict == None else conncetdict
        self.db = pymysql.connect(
                host='localhost',
                user='root',
                password=self.conncetdict.get("password",'Zqlmm0223!'),
                database=self.conncetdict.get("database",'ninjamustdie_global'),
                port=self.conncetdict.get("port",3306)
        )
    def insert_data(self,table_name,set_dict,where_dict):
        cursorInsert = self.db.cursor()
        insert_dict = where_dict.copy()
        insert_dict.update(set_dict)
        insert_keys = str(insert_dict.keys()).replace("dict_keys([","").replace("])","").replace("'","`")
        insert_values = list(insert_dict.values())
        insert_into = """insert into {} ({}) values({})""".format(table_name,insert_keys,','.join(['%s']*len(insert_values)))
        try:
            cursorInsert.execute(insert_into,insert_values)
            self.db.commit()
            cursorInsert.close()
        except Exception as insert_error:
            if '1062' in str(insert_error):
                self.db.rollback()
                self.update_data(table_name=table_name,set_dict=set_dict,where_dict=where_dict)
            else:
                print(insert_error, '\n', insert_dict)
    def update_data(self,table_name,set_dict,where_dict):
        cursorUpdate = self.db.cursor()
        set_1 = ""
        where_1 =""
        for set_item in set_dict.items():
            if set_item[1] == None:
                set_1 += "`" + str(set_item[0]) + "` = Null,"
            else:
                set_1 += "`" + str(set_item[0]) + "` = '" + str(set_item[1]) + "',"
        for where_item in where_dict.items():
            where_1+= "`"+str(where_item[0])+"` = '"+str(where_item[1])+"' and "
        update = """update `{}` set {} where {}""".format(table_name,set_1[:-1],where_1[:-4])
        try:
            cursorUpdate.execute(update)
            self.db.commit()
            cursorUpdate.close()
        except Exception as update_error:
            print('update_error\n',update_error,'\n',update)
    def search_data(self,select_table):
        cursorSearch = self.db.cursor()
        cursorSearch.execute(select_table)
        fetchall_data = cursorSearch.fetchall()
        self.db.commit()
        cursorSearch.close()
        return fetchall_data
    def test(self):
        print('调用成功')
    def cursor_update(self,tableInfo):
        cursorU = self.db.cursor()
        cursorU.execute(tableInfo)
        self.db.commit()
        cursorU.close()