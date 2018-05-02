from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
from nltk.tokenize import word_tokenize
import nltk
import re
import sys
from unidecode import unidecode
import string
from autocorrect import spell

def process_with_fetch():
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        cursor.execute(" SELECT class, SIT FROM data_original")
        row = cursor.fetchall()

        for item in row:
            sentence = item[1].lower()
            newstring = re.sub('[^A-Za-z0-9 ]+', '', sentence)
            newstring = re.sub('\d+', '', newstring)
            newstring = unidecode(newstring)
            #Lowercasing
            print(newstring)
            word_tokens = word_tokenize(newstring)
            last_string = ""
            for w in word_tokens:
                w = spell(w)
                last_string += " " + w
            result = cursor.execute("INSERT INTO data_maxentropy(class, sentence) VALUES(%s, %s)", (item[0], last_string))

    except Error as e:
        print(e)

    finally:
        conn.commit()
        cursor.close()
        conn.close()

if __name__ == '__main__':
    process_with_fetch()