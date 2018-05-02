from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
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
        cursor.execute(" SELECT * FROM data_maxentropy")
        row = cursor.fetchall()
        # print("masuk")

        for item in row:
            #Removing punctuation and special char
            newstring = item[2].lower()
            newstring = re.sub('[^A-Za-z0-9 ]+', '', newstring)
            #Removing digit
            # newstring = ' '.join(newstring.strip(string.punctuation) for word in newstring.split())
            newstring = re.sub('\d+', '', newstring)
            newstring = unidecode(newstring)
            #Lowercasing
            # Tokenizing
            word_tokens = word_tokenize(newstring)
            filtered_sentence = [w for w in word_tokens if not w in stop_words] 
            
            filtered_sentence = []
            last_string = ""
            other_noises = ['st', 'nd', 'rd', 'th', 'one', 'two',
                             'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'second', 'seconds', 'minute',
                               'minutes', 'hour', 'hours', 'days', 'month', 'year']
            exception_word = ['go', 'ok']
            lmtzr = WordNetLemmatizer()     
            for w in word_tokens:
                check = False
                w = spell(w)
                temp = lmtzr.lemmatize(w, 'a')
                if(temp != w):
                    check = True
                if(not check):
                    temp = lmtzr.lemmatize(w, 'v')
                    if(temp != w):
                        check = True
                    if(not check):
                        temp = lmtzr.lemmatize(w)
                w = temp
                if w not in stop_words and w not in other_noises and len(w) > 2:
                    last_string += " "+ w
                elif w not in stop_words and w not in other_noises and len(w) == 2 and w in exception_word:
                    last_string += " "+ w
            print(item[0])
            result = cursor.execute(" UPDATE data_maxentropy SET sentence=%s WHERE id=%s ",(last_string, item[0]))

    except Error as e:
        print(e)

    finally:
        conn.commit()
        cursor.close()
        conn.close()

if __name__ == '__main__':
    stop_words = set(stopwords.words('english'))
    process_with_fetch()