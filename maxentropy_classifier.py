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
import numpy as np
def process_with_fetch():
	try:
		dbconfig = read_db_config()
		conn = MySQLConnection(**dbconfig)
		cursor = conn.cursor()
		cursor.execute(" SELECT * FROM data2 WHERE id < 10")
		row = cursor.fetchall()
		cursor.execute("SELECT * FROM data2 WHERE id >= 7001")
		test = cursor.fetchall()
		
		training_set = []
		for item in row:
			word_tokens = word_tokenize(item[5])
			other_noises = ['st', 'nd', 'rd', 'th', 'one', 'two',
			'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'second', 'seconds', 'minute',
			'minutes', 'hour', 'hours', 'days', 'month', 'year']
			exception_word = ['go', 'ok']
			lmtzr = WordNetLemmatizer()
			sentence = []
			for w in word_tokens:
				if w not in stop_words and w not in other_noises and len(w) > 2:
					sentence.append(w)
				elif w not in stop_words and w not in other_noises and len(w) == 2 and w in exception_word:
					sentence.append(w)
			sentence = dict([(word, True) for word in sentence])
			print(sentence)
			training_set.append([sentence, item[1]])
			numIterations = 100
		algorithm = nltk.classify.MaxentClassifier.ALGORITHMS[1]
		classifier = nltk.MaxentClassifier.train(training_set, algorithm, max_iter=numIterations)
		classifier.show_most_informative_features(10)

		test_set = []
		for item in test:
			word_tokens = word_tokenize(item[5])
			test_sentence = []
			for w in word_tokens:
				if w not in stop_words and w not in other_noises and len(w) > 2:
					test_sentence.append(w)
				elif w not in stop_words and w not in other_noises and len(w) == 2 and w in exception_word:
					test_sentence.append(w)
			test_sentence = dict([(word, True) for word in sentence])
			print(test_sentence)
			test_set.append([test_sentence, item[1]])
		print(test_set)
		for item in test_set:
			label = item[1]
			text = item[0]
			determined_label = classifier.classify(text)
			print determined_label, label

	except Error as e:
		print(e)

	finally:
		conn.commit()
		cursor.close()
		conn.close()

if __name__ == '__main__':
    stop_words = set(stopwords.words('english'))
    process_with_fetch()