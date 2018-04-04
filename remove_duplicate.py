from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
import re

def removeDuplicate():
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor(buffered=True)
        
        cursor.execute("SELECT * from data")
        result = cursor.fetchall()
        sentences_list = []
        for res in result:
            print(res[5])
            target = re.sub('^\s', '', res[5])
            strip_word = re.sub('\s$', '', target)

            target = '%'+strip_word+'%'
            print(target)
            cursor.execute("SELECT * from data2 WHERE SIT=%(target)s ", {'target':target})
            check = cursor.fetchall()
            if target not in sentences_list:
                sentences_list.append(target)
                cursor.execute("INSERT INTO data2 VALUES(%(id)s, %(class)s, %(f3)s, %(f4)s, %(mkey)s, %(sit)s, \
                %(state)s)", {'id':res[0], 'class':res[1], 'f3':res[2], 'f4':res[3], 'mkey':res[4], 'sit':strip_word, \
                'state': res[6]})
            # break
    except Error as e:
        print(e)
    finally:
        conn.commit()
        cursor.close()
        conn.close()

if __name__ == '__main__':
    removeDuplicate()