from mysql.connector import MySQLConnection, Error
from nltk.tokenize import word_tokenize
from python_mysql_dbconfig import read_db_config
from sklearn import linear_model
from sklearn import metrics
# from sklearn.model_selection import cross_val_score
# from sklearn.cross_validation import train_test_split
import pandas as pd
import numpy as np


def process_words():
	try:
		dbconfig = read_db_config()
		conn = MySQLConnection(**dbconfig)
		cursor = conn.cursor(buffered=True)

		# CREATE EMPTY BOW
		cursor.execute("SELECT * FROM dictionary_maxentropy")
		words = cursor.fetchall()

		cursor.execute("SELECT * FROM data3 where id <= 7000")
		data_train = cursor.fetchall()
		print(len(words))
		print(len(data_train))

		train_bow = np.zeros((len(data_train), len(words)+1), dtype=int)

		index = 0
		for item in data_train:
			sentence = word_tokenize(item[2])
			for w in sentence:
				cursor.execute("SELECT id FROM dictionary_maxentropy WHERE word=%(w)s", {"w": w})
				result = cursor.fetchone()
				train_bow[index][result[0]] += 1
			train_bow[index][0] = item[1]
			index += 1
		# e[:, 1:5]


		cursor.execute("SELECT * FROM data3 where id > 7000")
		data_test = cursor.fetchall()
		test_bow = np.zeros((len(data_test), len(words)+1), dtype=int)
		
		index = 0
		for item in data_test:
			print(item[2])
			sentence = word_tokenize(item[2])
			for w in sentence:
				cursor.execute("SELECT id FROM dictionary_maxentropy WHERE word=%(w)s", {"w": w})
				result = cursor.fetchone()
				test_bow[index][result[0]] += 1
			test_bow[index][0] = item[1]
			index += 1
		return train_bow, test_bow

	
	except Exception as e:
		print(e)
	finally:
		conn.commit()
		cursor.close()
		conn.close()
		return train_bow, test_bow

def train_classifier(data_train, data_test):
    lr = linear_model.LogisticRegression()
    mul_lr = linear_model.LogisticRegression(multi_class='multinomial', solver='newton-cg').fit(data_train[:,1:], data_train[:,0])
    lr.fit(data_train[:,1:], data_train[:,0])

    print "Logistic regression Train Accuracy :: ", metrics.accuracy_score(data_train[:,0], lr.predict(data_train[:,1:]))
    print "Logistic regression Test Accuracy :: ", metrics.accuracy_score(data_test[:,0], lr.predict(data_test[:,1:]))
    
    print "Multinomial Logistic regression Train Accuracy :: ", metrics.accuracy_score(data_train[:,0], mul_lr.predict(data_train[:,1:]))
    print "Multinomial Logistic regression Test Accuracy :: ", metrics.accuracy_score(data_test[:,0], mul_lr.predict(data_test[:,1:]))

if __name__ == '__main__':
	data_train, data_test = process_words()
	train_classifier(data_train, data_test)