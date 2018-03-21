from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import re
import sys

def process_with_fetch():
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        cursor.execute(" SELECT * FROM bag_of_words")
        row = cursor.fetchall()
        print("masuk")

        for item in row:
            newstring = re.sub('^\d+\s|\s\d+\s|\s\d+$', '', item[1])
            print(newstring)
            # print(item[0])
            result = cursor.execute(" UPDATE bag_of_words SET words=%s WHERE id=%s ",
            (newstring, item[0]))
            print(result)      

    except Error as e:
        print(e)

    finally:
        conn.commit()
        cursor.close()
        conn.close()

if __name__ == '__main__':
    process_with_fetch()