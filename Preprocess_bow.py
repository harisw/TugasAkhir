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
from progress.bar import FillingCirclesBar as fcb
from nltk.tag import StanfordNERTagger as nerTagger

def preprocess():
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        cursor.execute("TRUNCATE preprocessed_data")
        cursor.execute("SELECT * FROM cleaned_data_original")
        row = cursor.fetchall()
        stop_words = set(stopwords.words('english'))
        st = nerTagger('knowledge_based/classifiers/english.all.3class.distsim.crf.ser.gz', 'knowledge_based/stanford-ner-3.9.1.jar')
        new_stopwords = getStopwords()
        pb = fcb("Preprocessing words ", max=len(row))
        for item in row:
            # print item[0]
            #Removing punctuation and special char
            newstring = item[2].lower()
            newstring = re.sub('[^A-Za-z0-9 ]+', '', newstring)
            #Removing digit
            newstring = re.sub('\d+', '', newstring)
            newstring = unidecode(newstring)
            word_tokens = word_tokenize(newstring)
            # filtered_sentence = [w for w in word_tokens if not w in stop_words] 
            # filtered_sentence = []
            last_string = ""
            # other_noises = ['st', 'nd', 'rd', 'th', 'one', 'two',
            #                  'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'second', 'seconds', 'minute',
            #                    'minutes', 'hour', 'hours', 'days', 'month', 'year', 'ois', 'etc', 'may', 'uni', 'PUC', 'yet',
            #                    'sri', 'Cou', 'fot','ive', 'ano', 'itd', 'usa', 'itd', 'Nev', 'Mai',
            #                    'ist', 'ger', 'hed', 'ufa']
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
                # ner_check = st.tag([w])
                # if ner_check[0][1] == 'O':
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
                if w not in stop_words and w not in new_stopwords and len(w) > 2:
                    last_string += " "+ w
                elif w not in stop_words and w not in new_stopwords and len(w) == 2 and w in exception_word:
                    last_string += " "+ w
            # print last_string
            if item[1] == "joy":
                new_class = 1
            elif item[1] == "fear":
                new_class = 2
            elif item[1] == "anger":
                new_class = 3
            elif item[1] == "sadness":
                new_class = 4
            elif item[1] == "disgust":
                new_class = 5
            elif item[1] == "shame":
                new_class = 6
            cursor.execute("INSERT INTO preprocessed_data VALUES(%s, %s, %s) ", (item[0], new_class, last_string))
            pb.next()
        pb.finish()
    except Error as e:
        print(e)

    finally:
        conn.commit()
        cursor.close()
        conn.close()

def getStopwords():
    import glob
    file_names = glob.glob("*.txt")
    my_stopwords = []
    for name in file_names:
        with open(name, 'r') as file:
            temp = file.readlines()
        my_stopwords += temp
    return my_stopwords