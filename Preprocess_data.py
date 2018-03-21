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
        class_list = ['joy', 'fear', 'anger', 'sadness', 'disgust', 'shame', 'guilt']
        for target in class_list:
            cursor.execute("SELECT * FROM data WHERE Field1='%s' " % (target))
            row = cursor.fetchall()
            print("Class %s has %s instances\n" % (target, len(row)))
            # print("masuk")

            for item in row:
                newstring = re.sub('[^A-Za-z0-9 ]+', '', item[5])
                print(newstring)
                word_tokens = word_tokenize(newstring)
                filtered_sentence = [w for w in word_tokens if not w in stop_words] 
                filtered_sentence = []
                last_string = ""
                for w in word_tokens:
                    if w not in stop_words:
                        # filtered_sentence.append(w)
                        last_string += " "+ w
                print(last_string)
                print(item[5])
                result = cursor.execute(" UPDATE data SET SIT=%s WHERE id=%s ",
                (last_string, item[0]))
                print(result)      

    except Error as e:
        print(e)

    finally:
        conn.commit()
        cursor.close()
        conn.close()

if __name__ == '__main__':
    stop_words = set(stopwords.words('english'))
    process_with_fetch()