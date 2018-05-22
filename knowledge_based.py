from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
from treetagger import TreeTagger
from unidecode import unidecode
from pprint import pprint
from treetaggerwrapper import TreeTagger 
from nltk.parse.stanford import StanfordParser 
from nltk.tag import StanfordNERTagger as nerTagger 
from nltk.tokenize import word_tokenize
from wnaffect import WNAffect
from emotion import Emotion
import os
from collections import defaultdict
from nltk.corpus import wordnet as wn
import treetaggerwrapper
from progress.bar import FillingCirclesBar as fcb
import numpy as np

def predict(target_id):
    try: 
        dbconfig = read_db_config() 
        conn = MySQLConnection(**dbconfig) 
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cleaned_data_original where id = %(target)s", {'target': str(target_id)})
        query_res = cursor.fetchone()
        sentence = query_res[2]
        tt = TreeTagger(TAGLANG='en')
        english_parser = StanfordParser('knowledge_based/stanford-parser.jar', 'knowledge_based/stanford-parser-3.9.1-models.jar')
        st = nerTagger('knowledge_based/classifiers/english.muc.7class.distsim.crf.ser.gz', 'knowledge_based/stanford-ner-3.9.1.jar')
        wna = WNAffect('knowledge_based/wordnet1.6/', 'knowledge_based/wordnetAffect/')

        tags = tt.tag_text(sentence)
        tags = treetaggerwrapper.make_tags(tags)
        parser_result = english_parser.raw_parse(sentence) 
        ner_result = st.tag(word_tokenize(sentence))
        emotions = ""
        check = 0
        check_emo = 0

        emotion_map = mapEmotions()
        emotion_score = np.zeros([2, 7], dtype=int)

        emotion_list = ""
        for i in range(0, 7):
            emotion_score[0][i] = i
        for word in tags:
            emo = wna.get_emotion(word[0], word[1])
            if emo != None:
                emotion_list += str(emo)+" "
                if check_emo == 0:
                    check_emo = 1
                result = lookUp(str(emo), emotion_map)
                if result != 0:
                    emotion_score[1][result] += 1
        # print emotion_map
        with open('ensemble_result.txt', 'a') as kb_file:
            kb_file.write("knowledge_based "+emotion_list)
        if check_emo != 0:
            result_index = np.unravel_index(np.argmax(emotion_score[1], axis=None), emotion_score[1].shape)
            return result_index[0]
        else:
            return 0
    except Error as e: 
        print(e)
    finally: 
        conn.commit() 
        cursor.close() 
        conn.close()

def lookUp(emotion, mymap):
    if emotion in mymap["joy"]:
        return 1
    elif emotion in mymap["fear"]:
        return 2
    elif emotion in mymap["anger"]:
        return 3
    elif emotion in mymap["sadness"]:
        return 4
    elif emotion in mymap["disgust"]:
        return 5
    elif emotion in mymap["shame"]:
        return 6
    else:
        return 0
def mapEmotions():
    emotions = {}
    with open('joy_mapping.txt', 'r') as file:
        mapping = file.read()
        mapping = mapping.split(',')
        emotions["joy"] = mapping
    with open('fear_mapping.txt', 'r') as file:
        mapping = file.read()
        mapping = mapping.split(',')
        emotions["fear"] = mapping
    with open('anger_mapping.txt', 'r') as file:
        mapping = file.read()
        mapping = mapping.split(',')
        emotions["anger"] = mapping
    with open('sadness_mapping.txt', 'r') as file:
        mapping = file.read()
        mapping = mapping.split(',')
        emotions["sadness"] = mapping
    with open('disgust_mapping.txt', 'r') as file:
        mapping = file.read()
        mapping = mapping.split(',')
        emotions["disgust"] = mapping
    with open('shame_mapping.txt', 'r') as file:
        mapping = file.read()
        mapping = mapping.split(',')
        emotions["shame"] = mapping
    return emotions

def findMax(emotion_counter):
    curr_max = 0
    result = 0
    for i in range(0,7):
        if emotion_counter[i] > curr_max:
            result = i
            curr_max = emotion_counter[i]
    return result