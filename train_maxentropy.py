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
	data_train = bow_vector
	# data_test = bow_vector[6001:, :]
	# bnb = BernoulliNB(alpha=0.01).fit(data_train[:,2:], data_train[:, 0])
	# newton_lr = linear_model.LogisticRegression(solver='newton-cg', n_jobs=2).fit(data_train[:, 2:], data_train[:, 0])
	# a = 0.01
	alphas = [1, 0.5, 0.25, 0.1, 0.05, 0.025, 0.01, 0.005, 0.0025, 0.001]
	# newton_lr = linear_model.LogisticRegression(solver='newton-cg', n_jobs=2).fit(data_train[:, 2:], data_train[:, 0])
	# newton_lr_score = accuracy_score(newton_lr.predict(data_train[:,2:]), data_train[:,0])
	# for i in range(0,10):
	alphas = [0.0005, 0.00025, 0.0001]
	for a in alphas:
		bnb = BernoulliNB(alpha=a)
		# bnb_score = accuracy_score(bnb.predict(data_train[:,2:]), data_train[:, 0])
		bnb_score = cross_val_score(bnb, data_train[:,2:], data_train[:, 0], cv=10, verbose=1)
		with open('learning_result.txt', 'a') as file:
			file.write("\nalpha :: "+ str(a))
			file.write("\nBernoulliNB Crossvalidation Accuracy :: "+ str(bnb_score.mean()))

	alphas = [1, 0.5, 0.25, 0.1, 0.05, 0.025, 0.01, 0.005, 0.0025, 0.001, 0.0005, 0.00025, 0.0001]
	for a in alphas:
		bnb = BernoulliNB(alpha=a).fit(data_train[:,2:], data_train[:, 0])
		bnb_score = accuracy_score(bnb.predict(data_train[:,2:]), data_train[:, 0])
		# bnb_score = cross_val_score(bnb, data_train[:,2:], data_train[:, 0], cv=10, verbose=1)
		with open('learning_result.txt', 'a') as file:
			file.write("\nalpha :: "+ str(a))
			file.write("\nBernoulliNB Training Accuracy :: "+ str(bnb_score.mean()))
		# print "\nalpha :: ", a
		# print "\nBernoulliNB Train Accuracy :: ", bnb_score.mean()
	# newton_lr = linear_model.LogisticRegression(solver='newton-cg', n_jobs=2)
	# print data_train[2]
	# bnb_score = cross_val_score(bnb, data_train[:,2:], data_train[:, 0], cv=10, verbose=1)
	# nlr_score = cross_val_score(newton_lr, data_train[:,2:], data_train[:, 0], cv=10, verbose=1)
	# print "\nNewton LR Train Accuracy :: ", nlr_score

	# mnb_score = cross_val_score(mnb, data_train[:,1:], data_train[:, 0], cv=10, verbose=1)
	# TESTING PHASE
	# true_number = 0
	# total_number = len(data_test)
	# total_number = 2
	# progressbar = fcb("Testing Data ", max=total_number)
	# for item in data_test:
	# 	print item[1]
	# 	score_table = np.zeros([2, 7], dtype=int)
	# 	for i in range(0, 7):
	# 		score_table[0][i] = i
	# 	nb_result = bnb.predict([item[2:]])
	# 	lr_result = newton_lr.predict([item[2:]])
	# 	kb_result = kb.predict(item[1])

	# 	score_table[1][nb_result] += 1
	# 	score_table[1][lr_result] += 1
	# 	score_table[1][kb_result] += 1

	# 	predicted = np.unravel_index(np.argmax(score_table, axis=None), score_table.shape)
	# 	if predicted[1] == item[0]:
	# 		true_number += 1
	# 	with open('ensemble_result.txt', 'w') as file:
	# 		file.write(str(item[0]))
	# 		file.write(" || ")
	# 		file.write(str(score_table))
	# 		file.write("\n")
	# 		file.write("END RESULT\n")
	# 	progressbar.next()
	# progressbar.finish()
	# print "\nAccuracy :: ", (float(true_number)/float(total_number))
	return
	# mnb_nonfit = MultinomialNB(fit_prior=False)
	# bnb_nonfit = BernoulliNB(fit_prior=False)
	# mnb_score = cross_val_score(mnb, data_train[:,1:], data_train[:, 0], cv=10, verbose=1)
	# bnb_score = cross_val_score(bnb, data_train[:,1:], data_train[:, 0], cv=10, verbose=1)
	# mnb_score_nonfit = cross_val_score(mnb_nonfit, data_train[:,1:], data_train[:, 0], cv=10, verbose=1)
	# bnb_score_nonfit = cross_val_score(bnb_nonfit, data_train[:,1:], data_train[:, 0], cv=10, verbose=1)
	# print "\nMultinomialNB mean :: ", mnb_score.mean()
	# print "\nBernoulliNB mean :: ", bnb_score.mean()
	# print "\nMultinomialNB NonFit mean :: ", mnb_score_nonfit.mean()
	# print "\nBernoulliNB NonFit mean :: ", bnb_score_nonfit.mean()
	# y_pred = gnb.fit(iris.data, iris.target).predict(iris.data)
	# print("Number of mislabeled points out of a total %d points : %d"% (iris.data.shape[0],(iris.target != y_pred).sum()))
	# newton_lr = linear_model.LogisticRegression(solver='newton-cg', n_jobs=2)
	# lib_linear_lr = linear_model.LogisticRegression(n_jobs=2)
	# mul_lr1 = linear_model.LogisticRegression(multi_class='multinomial', solver='sag', n_jobs=2)
	# mul_lr2 = linear_model.LogisticRegression(multi_class='multinomial', solver='newton-cg', n_jobs=2)
	# mul_lr3 = linear_model.LogisticRegression(multi_class='multinomial', solver='saga', n_jobs=2)
	# mul_lr4 = linear_model.LogisticRegression(multi_class='multinomial', solver='lbfgs', n_jobs=2)
	# newton_lr_score = cross_val_score(newton_lr, data_train[:,1:], data_train[:,0], cv=10)
	# lib_lr_score = cross_val_score(lib_linear_lr, data_train[:,1:], data_train[:,0], cv=10)
	# mul_lr1_score = cross_val_score(mul_lr1, data_train[:,1:], data_train[:,0], cv=10)
	# mul_lr2_score = cross_val_score(mul_lr2, data_train[:,1:], data_train[:,0], cv=10)
	# mul_lr3_score = cross_val_score(mul_lr3, data_train[:,1:], data_train[:,0], cv=10)
	# mul_lr4_score = cross_val_score(mul_lr4, data_train[:,1:], data_train[:,0], cv=10)
	# print "Newton Linear Regression mean :: ", newton_lr_score.mean()
	# print "Lib Linear Regression mean :: ", lib_lr_score.mean()
	# print "Sag Multinomial Regression mean :: ", mul_lr1_score.mean()
	# print "Multinomial Regression mean :: ", mul_lr2_score.mean()
	# print "Saga Multinomial Regression mean :: ", mul_lr3_score.mean()
	# print "LBFGS Multinomial Regression mean :: ", mul_lr4_score.mean()

# if __name__ == '__main__':
# 	data_train = process_words()
# 	train_classifier(data_train)