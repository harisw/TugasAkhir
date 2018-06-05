from mysql.connector import MySQLConnection, Error
from nltk.tokenize import word_tokenize
from python_mysql_dbconfig import read_db_config
from sklearn import linear_model
from sklearn import metrics
from sklearn.model_selection import cross_val_score
from progress.bar import IncrementalBar
import numpy as np
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import BernoulliNB
import knowledge_based as kb
from progress.bar import FillingCirclesBar as fcb
from sklearn.metrics import accuracy_score

def processWords():
	try:
		dbconfig = read_db_config()
		conn = MySQLConnection(**dbconfig)
		cursor = conn.cursor(buffered=True)

		# CREATE EMPTY BOW
		cursor.execute("SELECT * FROM dictionary")
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
				cursor.execute("SELECT id FROM dictionary WHERE word=%(w)s", {"w": w})
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
	bow_vector, words_num = processWords()
	temp = bow_vector[:start_test, :]
	data_train = bow_vector[end_test:, :]
	data_train = np.concatenate((data_train, temp), axis=0)
	data_test = bow_vector[start_test:end_test, :]
	count = 0
	bnb = BernoulliNB(alpha=0.01).fit(data_train[:, 2:], data_train[:, 0])
	lr = linear_model.LogisticRegression(solver='newton-cg', n_jobs=2, max_iter=350).fit(data_train[:, 2:], data_train[:, 0])
	total_test = 0
	true_number = 0
	for item in data_test:
		score_table = np.zeros([2, 7], dtype=int)
		if str(item[1]) != '0':
			print item[1]
			total_test += 1
			result_nb = bnb.predict([item[2:]])
			result_lr = lr.predict([item[2:]])
			result_kb = kb.predict(item[1])
			
			score_table[1][result_nb] += 1 
			score_table[1][result_lr] += 1 
			if result_kb != 0: 
				score_table[1][result_kb] += 1
			predicted = np.unravel_index(np.argmax(score_table, axis=None), score_table.shape)
			final_prediction = predicted[1]
			if score_table[1][predicted[1]] == 1: 
				final_prediction = result_nb 
			if final_prediction == item[0]: 
				true_number += 1

			if item[0] != final_prediction:
				with open('ensemble_result.txt', 'a') as file:
					file.write("\n ID :: "+ str(item[1]))
					file.write(" :: Real "+ str(item[0]))
					file.write(" :: Predicted "+ str(predicted[1]))
	print "\n True :: ", true_number
	print "\n from :: ", total_test
	print "\nAccuracy :: ", (float(true_number) / float(total_test))
	return