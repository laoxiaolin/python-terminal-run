import logging
import sqlite3
from pathlib import Path

from config import config


db_info = config.db_info
db_file = db_info['path'] / db_info['name']
conn = sqlite3.connect(str(db_file))
db = conn.cursor()
logging.info('连接本地sqlite数据：{}'.format(db_file.resolve()))

def create_table(table_name, sql):
    if not is_table_exist(table_name):
        db.execute(sql)
        logging.info('创建新表: {}'.format(table_name))

# 读取多条记录
def query(sql):
    db.execute(sql)
    data = db.fetchall()
    return data

# 多条记录同时插入
def insert_many(table_name, sql, data, duplicate_field=None, tuple_num=None):
    if len(data)>0:
        data = delete_duplicate(table_name, duplicate_field, data, tuple_num)   #根据图片地址排重
        db.executemany(sql, data)
        conn.commit()
    logging.info('批量视频数据插入到数据库完毕！排除图片唯一性后，共有{}条记录被插入'.format(len(data)))

# 单条记录插入
def insert_one(table_name, data, duplicate_field=None):
    name, img, url, actor = data
    if not url_unique(table_name, duplicate_field ,url):
        sql = 'INSERT INTO {}(name, img, url, actor) VALUES(?,?,?,?)'.format(table_name)
        db.execute(sql, data)
        conn.commit()
        logging.info('one视频数据插入到数据库完毕！')
    else:
        logging.info('数据已经存在！')

# 判断表是否存在
def is_table_exist(table_name):
    is_exist = True
    # 判断表是否存在
    sql = 'SELECT COUNT(*) FROM sqlite_master where type="table" and name=?'
    db.execute(sql, (table_name,))
    result = db.fetchone()[0]
    if result==0:
        is_exist = False
    
    return is_exist

# 判断唯一性
def url_unique(table_name, filed, value):
    is_unique = True
    sql = 'SELECT COUNT(*) FROM {} WHERE {}=?'.format(table_name, filed)
    db.execute(sql, (value,))
    result = db.fetchone()[0]
    if result == 0:
        is_unique = False

    return is_unique

# 保证新抓取的视频网址唯一性。删除数组中已有的重复值
def delete_duplicate(table_name, filed, data, tuple_num=None):
    if type(data) == tuple:
        [data.remove(v) for v in data if url_unique(table_name, filed, v[tuple_num])]
    return data


def close_all():
    db.close()
    conn.close()

# if __name__ == '__main__':
#     pass