from mysql.connector import MySQLConnection, Error
from nltk.tokenize import word_tokenize
from python_mysql_dbconfig import read_db_config
from sklearn import linear_model
from sklearn import metrics
from sklearn.model_selection import cross_val_score
from progress.bar import IncrementalBar
# from sklearn.cross_validation import train_test_split
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
		return train_bow

def classifying():
	# mnb = MultinomialNB()
	bow_vector = process_words()
	data_train = bow_vector[:6000]
	data_test = bow_vector[6001:, :]
	bnb = BernoulliNB(alpha=0.5).fit(data_train[:,2:], data_train[:, 0])
	newton_lr = linear_model.LogisticRegression(solver='newton-cg', n_jobs=2).fit(data_train[:, 2:], data_train[:, 0])

	# TESTING PHASE
	true_number = 0
	total_number = len(data_test)
	total_number = 2
	for item in data_test:
		print item[1]
		score_table = np.zeros([2, 7], dtype=int)
		for i in range(0, 7):
			score_table[0][i] = i
		nb_result = bnb.predict([item[2:]])
		lr_result = newton_lr.predict([item[2:]])
		kb_result = kb.predict(item[1])

		score_table[1][nb_result] += 1
		score_table[1][lr_result] += 1
		if kb_result != 0:
			score_table[1][kb_result] += 1

		predicted = np.unravel_index(np.argmax(score_table, axis=None), score_table.shape)
		if predicted[1] == item[0]:
			true_number += 1
		with open('ensemble_result.txt', 'a') as file:
			file.write("  "+str(item[0]))
			file.write(" || ")
			file.write(str(score_table))
			file.write("\n")
			file.write("END RESULT\n")
	print "\nAccuracy :: ", (float(true_number)/float(total_number))
	return