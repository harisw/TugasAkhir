from mysql.connector import MySQLConnection, Error
from nltk.tokenize import word_tokenize
from python_mysql_dbconfig import read_db_config
from sklearn import linear_model
from sklearn import metrics
from sklearn.model_selection import cross_val_score
from progress.bar import IncrementalBar
import pandas as pd
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import BernoulliNB
import knowledge_based as kb
from progress.bar import FillingCirclesBar as fcb
from sklearn.metrics import accuracy_score

def process_words():
	try:
		dbconfig = read_db_config()
		conn = MySQLConnection(**dbconfig)
		cursor = conn.cursor(buffered=True)

		# CREATE EMPTY BOW
		cursor.execute("SELECT * FROM dictionary_maxentropy")
		words = cursor.fetchall()

		cursor.execute("SELECT * FROM preprocessed_data")
		data_train = cursor.fetchall()

		bar = IncrementalBar('Processing Words', max=len(data_train))
		train_bow = np.zeros((len(data_train), len(words)+2), dtype=int)

		index = 0
		# FIRST COLUMN FOR CLASS, SECOND COLUMN FOR ID
		for item in data_train:
			sentence = word_tokenize(item[2])
			for w in sentence:
				cursor.execute("SELECT id FROM dictionary_maxentropy WHERE word=%(w)s", {"w": w})
				result = cursor.fetchone()
				train_bow[index][result[0]+2] += 1
			train_bow[index][0] = item[1]
			train_bow[index][1] = item[0]
			bar.next()
			index += 1
		bar.finish()
	
	except Exception as e:
		print(e)
	finally:
		conn.commit()
		cursor.close()
		conn.close()
		return train_bow, len(words)

def classifying():
	bow_vector, words_num = process_words()

		#RESHUFFLING DATA
	start = 0
	step = 412
	end = start + step
	for i in range(0, 14):
		if i == 0:
			data_train = bow_vector[step:, :]
			data_test = bow_vector[:end, :]
		elif i == 13:
			data_train = bow_vector[:start, :]
			data_test = bow_vector[start:, :]
		else:
			temp = bow_vector[:start, :]
			data_train = bow_vector[end:, :]
			data_train = np.concatenate((data_train, temp), axis=0)
			data_test = bow_vector[start:end, :]
		start += step
		end += step
		count = 0
		print len(data_train)
		print len(data_test)
		bnb = BernoulliNB(alpha=0.01).fit(data_train[:, 2:], data_train[:, 0])
		lr = linear_model.LogisticRegression(solver='newton-cg', n_jobs=2, max_iter=350).fit(data_train[:, 2:], data_train[:, 0])
		true_nb = 0
		true_lr = 0
		total_test = 0
		progressbar = fcb('Testing Process', max=len(data_test))
		for item in data_test:
			if str(item[1]) != '0':
				total_test += 1
				result = bnb.predict([item[2:]])
				result_lr = lr.predict([item[2:]])
				if item[0] == result:
					true_nb += 1
				if item[0] == result_lr:
					true_lr += 1
				
				if item[0] != result and item[0] != result_lr:
					with open('learning_result.txt', 'a') as file:
						file.write("\n ID :: "+ str(item[1]))
						file.write(" :: Real "+ str(item[0]))
						file.write(" :: Predicted"+ str(result_lr))
			progressbar.next()
		progressbar.finish()
		print "\n True :: ", true_nb
		print "\n from :: ", total_test
		print "\nAccuracy NB:: ", (float(true_nb) / float(total_test))
		print "\nAccuracy LR:: ", (float(true_lr) / float(total_test))
	return