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


def process_words():
	try:
		dbconfig = read_db_config()
		conn = MySQLConnection(**dbconfig)
		cursor = conn.cursor(buffered=True)

		# CREATE EMPTY BOW
		cursor.execute("SELECT * FROM dictionary_maxentropy")
		words = cursor.fetchall()

		cursor.execute("SELECT * FROM data3")
		data_train = cursor.fetchall()
		print(len(words))
		print(len(data_train))
		bar = IncrementalBar('Processing', max=len(data_train))
		train_bow = np.zeros((len(data_train), len(words)+1), dtype=int)

		index = 0
		for item in data_train:
			sentence = word_tokenize(item[2])
			for w in sentence:
				cursor.execute("SELECT id FROM dictionary_maxentropy WHERE word=%(w)s", {"w": w})
				result = cursor.fetchone()
				train_bow[index][result[0]] += 1
			train_bow[index][0] = item[1]
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

def train_classifier(data_train):
	# newton_lr = linear_model.LogisticRegression(solver='newton-cg', n_jobs=2)
	# lib_linear_lr = linear_model.LogisticRegression(n_jobs=2)
	# mul_lr1 = linear_model.LogisticRegression(multi_class='multinomial', solver='sag', n_jobs=2)
	# mul_lr2 = linear_model.LogisticRegression(multi_class='multinomial', solver='newton-cg', n_jobs=2)
	# mul_lr3 = linear_model.LogisticRegression(multi_class='multinomial', solver='saga', n_jobs=2)
	mul_lr4 = linear_model.LogisticRegression(multi_class='multinomial', solver='lbfgs', n_jobs=2)
	# newton_lr_score = cross_val_score(newton_lr, data_train[:,1:], data_train[:,0], cv=10)
	# lib_lr_score = cross_val_score(lib_linear_lr, data_train[:,1:], data_train[:,0], cv=10)
	# mul_lr1_score = cross_val_score(mul_lr1, data_train[:,1:], data_train[:,0], cv=10)
	# mul_lr2_score = cross_val_score(mul_lr2, data_train[:,1:], data_train[:,0], cv=10)
	# mul_lr3_score = cross_val_score(mul_lr3, data_train[:,1:], data_train[:,0], cv=10)
	mul_lr4_score = cross_val_score(mul_lr4, data_train[:,1:], data_train[:,0], cv=10)
	# print "Newton Linear Regression mean :: ", newton_lr_score.mean()
	# print "Lib Linear Regression mean :: ", lib_lr_score.mean()
	# print "Sag Multinomial Regression mean :: ", mul_lr1_score.mean()
	# print "Multinomial Regression mean :: ", mul_lr2_score.mean()
	# print "Saga Multinomial Regression mean :: ", mul_lr3_score.mean()
	print "LBFGS Multinomial Regression mean :: ", mul_lr4_score.mean()

if __name__ == '__main__':
	data_train = process_words()
	train_classifier(data_train)