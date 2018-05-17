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
        cursor.execute(" SELECT * FROM data3")
        row = cursor.fetchall()
        # print("masuk")

        for item in row:
            #Removing punctuation and special char
            newstring = item[2]
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
                               'minutes', 'hour', 'hours', 'days', 'month', 'year', 'ois', 'etc', 'may', 'uni', 'PUC', 'yet',
                               'sri', 'Cou', 'iii', 'fot', 'Bsc', 'Msc', 'UGC', 'ive', 'ano', 'itd', 'usa', 'itd', 'Nev', 'Mai',
                               'SSC', 'ist', 'ger', 'HSC', 'hed', 'ufa', 'IMF', 'UCB', 'VSP', 'IMC', 'eng', 'SYC', 'IAM', 'USC',
                               'BBQ', 'ICC', 'TBA', 'GPA', 'sima', 'Magda', 'andor', 'ter', 'many', 'thus', 'seem', 'LBHS', 'MSCE']
            exception_word = ['go', 'ok']
            lmtzr = WordNetLemmatizer()     
            for w in word_tokens:
                w = w.lower()
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
            print last_string
            result = cursor.execute(" UPDATE data3 SET sentence=%s WHERE id=%s ",(last_string, item[0]))

    except Error as e:
        print(e)

    finally:
        conn.commit()
        cursor.close()
        conn.close()

if __name__ == '__main__':
    stop_words = set(stopwords.words('english'))
    process_with_fetch()