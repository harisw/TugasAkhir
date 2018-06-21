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

def predict(target_id, tt, wna, cursor):
    # try:
    cursor.execute("SELECT * FROM cleaned_data_original where id = %(target)s", {'target': str(target_id)})
    query_res = cursor.fetchone()
    if query_res == None:
        return 0
    sentence = query_res[2]
    tags = tt.tag_text(sentence)
    tags = treetaggerwrapper.make_tags(tags)
    emotions = ""
    check = 0
    check_emo = 0

    emotion_map = mapEmotions()
    emotion_score = np.zeros([2, 7], dtype=int)
    relevant_tag = ['RB', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'JJ']
    for i in range(0, 3):
        emotion_score[0][i] = i
    for word in tags:
        if len(word) >= 2 and word[1] in relevant_tag:
            emo = wna.get_emotion(word[0], word[1])
            if emo != None:
                if check_emo == 0:
                    check_emo = 1
                result = lookUp(str(emo), emotion_map)
                if result != -1:
                    emotion_score[1][result] += 1
    # print emotion_map
    if check_emo != 0:
        result_index = np.unravel_index(np.argmax(emotion_score[1], axis=None), emotion_score[1].shape)
        return result_index[0]
    else:
        return -1
# except Error as e: 
#     print(e)
# finally:
    # conn.commit() 

def lookUp(emotion, mymap):
    if emotion in mymap["joy"]:
        return 1
    elif emotion in mymap["fear"] or emotion in mymap["anger"] or emotion in mymap["sadness"] or emotion in mymap["disgust"] or emotion in mymap["shame"]:
        return 0
    else:
        return -1
def mapEmotions():
    emotions = {}
    with open('notes/joy_mapping.txt', 'r') as file:
        mapping = file.read()
        mapping = mapping.split(',')
        emotions["joy"] = mapping
    with open('notes/fear_mapping.txt', 'r') as file:
        mapping = file.read()
        mapping = mapping.split(',')
        emotions["fear"] = mapping
    with open('notes/anger_mapping.txt', 'r') as file:
        mapping = file.read()
        mapping = mapping.split(',')
        emotions["anger"] = mapping
    with open('notes/sadness_mapping.txt', 'r') as file:
        mapping = file.read()
        mapping = mapping.split(',')
        emotions["sadness"] = mapping
    with open('notes/disgust_mapping.txt', 'r') as file:
        mapping = file.read()
        mapping = mapping.split(',')
        emotions["disgust"] = mapping
    with open('notes/shame_mapping.txt', 'r') as file:
        mapping = file.read()
        mapping = mapping.split(',')
        emotions["shame"] = mapping
    return emotions