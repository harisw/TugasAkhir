from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
import re
from progress.bar import FillingCirclesBar as fcb

def removeDuplicate():
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor(buffered=True)
        
        cursor.execute("SELECT * from data_original")
        result = cursor.fetchall()
        sentences_list = []
        progressbar = fcb('Cleaning Duplicate', max=len(result))
        for res in result:
            target = re.sub('^\s', '', res[5])
            strip_word = re.sub('\s$', '', target)

            target = '%'+strip_word+'%'
            if target not in sentences_list:
                sentences_list.append(target)
                result = cursor.execute("INSERT INTO cleaned_data_original(class, sentence) VALUES(%s, %s)", (res[1], strip_word))
                # cursor.execute("INSERT INTO data3(class, sentence) VALUES( %(class)s, %(f3)s, %(f4)s, %(mkey)s, %(sit)s, \
                # %(state)s)", {'id':res[0], 'class':res[1], 'f3':res[2], 'f4':res[3], 'mkey':res[4], 'sit':strip_word, \
                # 'state': res[6]})
            # break
            progressbar.next()
        progressbar.finish()
    except Error as e:
        print(e)
    finally:
        conn.commit()
        cursor.close()
        conn.close()

if __name__ == '__main__':
    removeDuplicate()