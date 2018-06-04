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
from progress.bar import FillingSquaresBar as fsb
from nltk.tag import StanfordNERTagger as nerTagger
import enchant

def begin():
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        cursor.execute("TRUNCATE preprocessed_data")
        cursor.execute("SELECT * FROM cleaned_data_original")
        isear_row = cursor.fetchall()
        cursor.execute("SELECT * FROM affective_text_original")
        affective_row = cursor.fetchall()
        all_data = isear_row + affective_row
        preprocess(all_data, cursor)
        registerBow(cursor)
    except Error as e:
        print(e)

    finally:
        conn.commit()
        cursor.close()
        conn.close()

def registerBow(cursor):
    cursor.execute("TRUNCATE dictionary")
    cursor.execute("ALTER TABLE dictionary AUTO_INCREMENT=1")
    cursor.execute("SELECT sentence FROM preprocessed_data")
    corpus = cursor.fetchall()
    word_list = []
    pb = fsb("Registering Bow ", max=len(corpus))
    for item in corpus:
        words = word_tokenize(item[0])
        for w in words:
            if w not in word_list:
                word_list.append(w)
                # print(w)
                cursor.execute("INSERT INTO dictionary (word) VALUE(%(myword)s)", {'myword': w })
        pb.next()
    pb.finish()
    return

def preprocess(row, cursor):
    stop_words = set(stopwords.words('english'))
    # st = nerTagger('knowledge_based/classifiers/english.all.3class.distsim.crf.ser.gz', 'knowledge_based/stanford-ner-3.9.1.jar')
    new_stopwords = getStopwords()
    #English checking
    eng_words = enchant.Dict("en_US")
    pb = fcb("Preprocessing words ", max=len(row))
    for item in row:
        #Removing punctuation and special char
        newstring = item[2].lower()
        newstring = re.sub('[^A-Za-z0-9 ]+', '', newstring)
        #Removing digit
        newstring = re.sub('\d+', '', newstring)
        newstring = unidecode(newstring)
        word_tokens = word_tokenize(newstring)
        filtered_sentence = []
        last_string = ""
        exception_word = ['go', 'ok']
        lmtzr = WordNetLemmatizer()     
        for w in word_tokens:
            w = w.lower()
            check = False
            w = spell(w)
            #Using NERTagger to check it's entity
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
            if w not in stop_words and w not in new_stopwords and eng_words.check(w):
                if len(w) > 2:
                    last_string += " "+ w
                    filtered_sentence.append(w)
                elif len(w) == 2 and w in exception_word:
                    last_string += " "+ w
                    filtered_sentence.append(w)
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
        if len(filtered_sentence) > 1:
            cursor.execute("INSERT INTO preprocessed_data (class, sentence) VALUES(%s, %s) ", (new_class, last_string))
        pb.next()
    pb.finish()
    return

def getStopwords():
    import glob
    file_names = glob.glob("*.txt")
    my_stopwords = []
    for name in file_names:
        with open(name, 'r') as file:
            temp = file.readlines()
        my_stopwords += temp
    return my_stopwords