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

def process_with_fetch():
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cleaned_data_original")
        row = cursor.fetchall()
        tt = TreeTagger(TAGLANG='en')
        english_parser = StanfordParser('knowledge_based/stanford-parser.jar', 'knowledge_based/stanford-parser-3.9.1-models.jar')
        st = nerTagger('knowledge_based/classifiers/english.muc.7class.distsim.crf.ser.gz', 'knowledge_based/stanford-ner-3.9.1.jar')
        wna = WNAffect('knowledge_based/wordnet1.6/', 'knowledge_based/wordnetAffect/')
        true_item = 0
        for item in row:
            print(item[0])
            sentence = item[2]
            tags = tt.tag_text(sentence)
            tags = treetaggerwrapper.make_tags(tags)
            parser_result = english_parser.raw_parse(sentence) 
            ner_result = st.tag(word_tokenize(sentence))
            emotions = ""
            check = 0
            check_emo = 0
            # print tags
            for word in tags:
                emo = wna.get_emotion(word[0], word[1])
                emotions += str(emo) + " "
                if emo == item[1]:
                    if check == 0:
                        check = 1
                        true_item += 1
                if check_emo == 0 and emo != None:
                    check_emo = 1
            with open('knowledge_based_result.txt', 'a') as target_file:
                target_file.write(item[1])
                target_file.write("  ")
                target_file.write(unidecode(item[2]))
                target_file.write(" || ")
                if check_emo == 1:
                    target_file.write(emotions)
                target_file.write("\n")
        accuracy = float(true_item) / float(len(row))
        print("\nAccuracy : {0:.4f}".format(accuracy))

    except Error as e:
        print(e)

    finally:
        conn.commit()
        cursor.close()
        conn.close()

if __name__ == '__main__':
	process_with_fetch()