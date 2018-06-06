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
from sklearn.metrics import precision_recall_fscore_support as prf
from treetaggerwrapper import TreeTagger 
from nltk.parse.stanford import StanfordParser 
from nltk.tag import StanfordNERTagger as nerTagger 
from nltk.tokenize import word_tokenize
from wnaffect import WNAffect
from emotion import Emotion

prefix = 'knowledge_based/'
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
	dbconfig = read_db_config()
	conn = MySQLConnection(**dbconfig)
	cursor = conn.cursor(buffered=True)

	start = 0
	step = 760
	end = start + step
    # english_parser = StanfordParser(prefix+'stanford-parser.jar', prefix+'stanford-parser-3.9.1-models.jar')
    # st = nerTagger(prefix+'classifiers/english.all.3class.distsim.crf.ser.gz', prefix+'stanford-ner-3.9.1.jar')
	tt = TreeTagger(TAGLANG='en')
	wna = WNAffect(prefix+'wordnet1.6/', prefix+'wordnetAffect/')
	for i in range(0, 10):
		if i == 0:
			data_train = bow_vector[step:, :]
			data_test = bow_vector[:end, :]
		elif i == 9:
			data_train = bow_vector[:start, :]
			data_test = bow_vector[start:, :]
		else:
			temp = bow_vector[:start, :]
			data_train = bow_vector[end:, :]
			data_train = np.concatenate((data_train, temp), axis=0)
			data_test = bow_vector[start:end, :]
		start += step
		end += step
		bnb = BernoulliNB(alpha=0.01).fit(data_train[:, 2:], data_train[:, 0])
		lr = linear_model.LogisticRegression(solver='newton-cg', n_jobs=3, max_iter=300).fit(data_train[:, 2:], data_train[:, 0])
		total_test = 0
		true_number = 0
		prediction = []
		for item in data_test:
			score_table = np.zeros([2, 3], dtype=int)
			if str(item[1]) != '0':
				print item[1]
				total_test += 1
				result_nb = bnb.predict([item[2:]])
				result_lr = lr.predict([item[2:]])
				result_kb = kb.predict(item[1], tt, wna, cursor)
				
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
				prediction.append(int(final_prediction))
		prediction = np.array(prediction)
		if i == 9:
			all_score = prf(data_test[:770,0], prediction, average='binary')
		else:
			all_score = prf(data_test[:,0], prediction, average='binary')
		with open('ensemble_result[var1].txt', 'a') as file:
			file.write("\n True :: "+str(true_number))
			file.write(" from :: "+str(total_test))
			file.write("\nAccuracy :: "+str((float(true_number) / float(total_test))))
			file.write("\nPrecision :: "+str(all_score[0]))
			file.write("\nRecall :: "+str(all_score[1]))
			file.write("\nF-Score :: "+str(all_score[2]))
	start = 0
	step = 760
	end = start + step
	for i in range(0, 10):
		if i == 0:
			data_train = bow_vector[step:, :]
			data_test = bow_vector[:end, :]
		elif i == 9:
			data_train = bow_vector[:start, :]
			data_test = bow_vector[start:, :]
		else:
			temp = bow_vector[:start, :]
			data_train = bow_vector[end:, :]
			data_train = np.concatenate((data_train, temp), axis=0)
			data_test = bow_vector[start:end, :]
		start += step
		end += step
		bnb = BernoulliNB(alpha=0.01).fit(data_train[:, 2:], data_train[:, 0])
		lr = linear_model.LogisticRegression(solver='liblinear', n_jobs=3, max_iter=300).fit(data_train[:, 2:], data_train[:, 0])
		total_test = 0
		true_number = 0
		prediction = []
		for item in data_test:
			score_table = np.zeros([2, 3], dtype=int)
			if str(item[1]) != '0':
				print item[1]
				total_test += 1
				result_nb = bnb.predict([item[2:]])
				result_lr = lr.predict([item[2:]])
				result_kb = kb.predict(item[1], tt, wna, cursor)
				
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
				prediction.append(int(final_prediction))
		prediction = np.array(prediction)
		if i == 9:
			all_score = prf(data_test[:770,0], prediction, average='binary')
		else:
			all_score = prf(data_test[:,0], prediction, average='binary')
		with open('ensemble_result[var2].txt', 'a') as file:
			file.write("\n True :: "+str(true_number))
			file.write(" from :: "+str(total_test))
			file.write("\nAccuracy :: "+str((float(true_number) / float(total_test))))
			file.write("\nPrecision :: "+str(all_score[0]))
			file.write("\nRecall :: "+str(all_score[1]))
			file.write("\nF-Score :: "+str(all_score[2]))
	start = 0
	step = 760
	end = start + step
	for i in range(0, 10):
		if i == 0:
			data_train = bow_vector[step:, :]
			data_test = bow_vector[:end, :]
		elif i == 9:
			data_train = bow_vector[:start, :]
			data_test = bow_vector[start:, :]
		else:
			temp = bow_vector[:start, :]
			data_train = bow_vector[end:, :]
			data_train = np.concatenate((data_train, temp), axis=0)
			data_test = bow_vector[start:end, :]
		start += step
		end += step
		bnb = MultinomialNB(alpha=0.01).fit(data_train[:, 2:], data_train[:, 0])
		lr = linear_model.LogisticRegression(solver='newton-cg', n_jobs=3, max_iter=300).fit(data_train[:, 2:], data_train[:, 0])
		total_test = 0
		true_number = 0
		prediction = []
		for item in data_test:
			score_table = np.zeros([2, 3], dtype=int)
			if str(item[1]) != '0':
				print item[1]
				total_test += 1
				result_nb = bnb.predict([item[2:]])
				result_lr = lr.predict([item[2:]])
				result_kb = kb.predict(item[1], tt, wna, cursor)
				
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
				prediction.append(int(final_prediction))
		prediction = np.array(prediction)
		if i == 9:
			all_score = prf(data_test[:770,0], prediction, average='binary')
		else:
			all_score = prf(data_test[:,0], prediction, average='binary')
		with open('ensemble_result[var3].txt', 'a') as file:
			file.write("\n True :: "+str(true_number))
			file.write(" from :: "+str(total_test))
			file.write("\nAccuracy :: "+str((float(true_number) / float(total_test))))
			file.write("\nPrecision :: "+str(all_score[0]))
			file.write("\nRecall :: "+str(all_score[1]))
			file.write("\nF-Score :: "+str(all_score[2]))
	start = 0
	step = 760
	end = start + step
	for i in range(0, 10):
		if i == 0:
			data_train = bow_vector[step:, :]
			data_test = bow_vector[:end, :]
		elif i == 9:
			data_train = bow_vector[:start, :]
			data_test = bow_vector[start:, :]
		else:
			temp = bow_vector[:start, :]
			data_train = bow_vector[end:, :]
			data_train = np.concatenate((data_train, temp), axis=0)
			data_test = bow_vector[start:end, :]
		start += step
		end += step
		bnb = MultinomialNB(alpha=0.01).fit(data_train[:, 2:], data_train[:, 0])
		lr = linear_model.LogisticRegression(solver='liblinear', n_jobs=3, max_iter=300).fit(data_train[:, 2:], data_train[:, 0])
		total_test = 0
		true_number = 0
		prediction = []
		for item in data_test:
			score_table = np.zeros([2, 3], dtype=int)
			if str(item[1]) != '0':
				print item[1]
				total_test += 1
				result_nb = bnb.predict([item[2:]])
				result_lr = lr.predict([item[2:]])
				result_kb = kb.predict(item[1], tt, wna, cursor)
				
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
				prediction.append(int(final_prediction))
		prediction = np.array(prediction)
		if i == 9:
			all_score = prf(data_test[:770,0], prediction, average='binary')
		else:
			all_score = prf(data_test[:,0], prediction, average='binary')
		with open('ensemble_result[var4].txt', 'a') as file:
			file.write("\n True :: "+str(true_number))
			file.write(" from :: "+str(total_test))
			file.write("\nAccuracy :: "+str((float(true_number) / float(total_test))))
			file.write("\nPrecision :: "+str(all_score[0]))
			file.write("\nRecall :: "+str(all_score[1]))
			file.write("\nF-Score :: "+str(all_score[2]))
	cursor.close()
	conn.close()
	return