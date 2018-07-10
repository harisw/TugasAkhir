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
def processWords(dataset):
	try:
		dbconfig = read_db_config()
		conn = MySQLConnection(**dbconfig)
		cursor = conn.cursor(buffered=True)

		# CREATE EMPTY BOW
		if dataset == 'isear':
			cursor.execute("SELECT * FROM dictionary_isear")
			words = cursor.fetchall()
			cursor.execute("SELECT * FROM preprocessed_isear")
			data_train = cursor.fetchall()
		elif dataset == 'affective':
			cursor.execute("SELECT * FROM dictionary_affectivetext")
			words = cursor.fetchall()
			cursor.execute("SELECT * FROM preprocessed_affectivetext")
			data_train = cursor.fetchall()
		else:
			cursor.execute("SELECT * FROM dictionary")
			words = cursor.fetchall()
			cursor.execute("SELECT * FROM preprocessed_data")
			data_train = cursor.fetchall()

		bar = IncrementalBar('Processing Words '+dataset, max=len(data_train))
		train_bow = np.zeros((len(data_train), len(words)+2), dtype=int)

		index = 0
		# FIRST COLUMN FOR CLASS, SECOND COLUMN FOR ID
		for item in data_train:
			sentence = word_tokenize(item[2])
			for w in sentence:
				if dataset == 'isear':
					cursor.execute("SELECT id FROM dictionary_isear WHERE word=%(w)s", {"w": w})
				elif dataset == 'affective':
					cursor.execute("SELECT id FROM dictionary_affectivetext WHERE word=%(w)s", {"w": w})
				else:
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
		return train_bow, len(words)

def classifyingCV():
	bow_isear, words_num = processWords('isear')
	dbconfig = read_db_config()
	conn = MySQLConnection(**dbconfig)
	cursor = conn.cursor(buffered=True)

	start = 0
	step = 760
	end = start + step
	tt = TreeTagger(TAGLANG='en')
	wna = WNAffect(prefix+'wordnet1.6/', prefix+'wordnetAffect/')
	for i in range(0, 10):
		if i == 0:
			data_train = bow_isear[step:, :]
			data_test = bow_isear[:end, :]
		elif i == 9:
			data_train = bow_isear[:start, :]
			data_test = bow_isear[start:, :]
			# new_test = data_test
		else:
			temp = bow_isear[:start, :]
			data_train = bow_isear[end:, :]
			data_train = np.concatenate((data_train, temp), axis=0)
			data_test = bow_isear[start:end, :]
		start += step
		end += step
		bnb = MultinomialNB(alpha=0.01).fit(data_train[:, 2:], data_train[:, 0])
		lr = linear_model.LogisticRegression(solver='liblinear', n_jobs=3).fit(data_train[:, 2:], data_train[:, 0])
		total_test = 0
		true_number = 0
		true_nb = 0
		true_lr = 0
		prediction_nb = []
		prediction_lr = []
		prediction = []

		for item in data_test:
			score_table = np.zeros([2, 3], dtype=int)
			if str(item[1]) != '0':
				print item[1]
				total_test += 1
				# ENSEMBLE
				result_nb = bnb.predict([item[2:]])
				result_lr = lr.predict([item[2:]])
				result_kb = kb.predict(item[1], tt, wna, cursor, 'isear')				
				score_table[1][result_nb] += 1 
				score_table[1][result_lr] += 1 
				if result_kb != 0: 
					score_table[1][result_kb] += 1
				predicted = np.unravel_index(np.argmax(score_table, axis=None), score_table.shape)
				final_prediction = predicted[1]
				if score_table[1][predicted[1]] == 1: 
					final_prediction = result_lr 
				if final_prediction == item[0]: 
					true_number += 1
				prediction.append(int(final_prediction))

				# SINGLE
				if result_nb == item[0]:
					true_nb += 1
				if result_lr == item[0]:
					true_lr += 1
				prediction_nb.append(int(result_nb))
				prediction_lr.append(int(result_lr))

			else:
				print item
		prediction = np.array(prediction)
		prediction_nb = np.array(prediction_nb)
		prediction_lr = np.array(prediction_lr)
		if i == 9:
			nb_score = prf(data_test[:665,0], prediction_nb, average='binary')
			lr_score = prf(data_test[:665,0], prediction_lr, average='binary')
			all_score = prf(data_test[:665,0], prediction, average='binary')
		else:
			nb_score = prf(data_test[:,0], prediction_nb, average='binary')
			lr_score = prf(data_test[:,0], prediction_lr, average='binary')
			all_score = prf(data_test[:,0], prediction, average='binary')
		with open('ensemble_result[isear].txt', 'a') as file:
			file.write("\n\n\nTrue :: "+str(true_number))
			file.write(" from :: "+str(total_test))
			file.write("\nAccuracy :: "+str((float(true_number) / float(total_test))))
			file.write("\nPrecision :: "+str(all_score[0]))
			file.write("\nF-Score :: "+str(all_score[2]))

			file.write("\nNB True :: "+str(true_nb))
			file.write(" from :: "+str(total_test))
			file.write("\nAccuracy :: "+str((float(true_nb) / float(total_test))))
			file.write("\nPrecision :: "+str(nb_score[0]))
			file.write("\nF-Score :: "+str(nb_score[2]))

			file.write("\nLR True :: "+str(true_lr))
			file.write(" from :: "+str(total_test))
			file.write("\nAccuracy :: "+str((float(true_lr) / float(total_test))))
			file.write("\nPrecision :: "+str(lr_score[0]))
			file.write("\nF-Score :: "+str(lr_score[2]))


	bow_affective, words_num = processWords('affective')
	start = 0
	step = 123
	end = start + step
	tt = TreeTagger(TAGLANG='en')
	wna = WNAffect(prefix+'wordnet1.6/', prefix+'wordnetAffect/')
	for i in range(0, 10):
		if i == 0:
			data_train = bow_affective[step:, :]
			data_test = bow_affective[:end, :]
		elif i == 9:
			data_train = bow_affective[:start, :]
			data_test = bow_affective[start:, :]
		else:
			temp = bow_affective[:start, :]
			data_train = bow_affective[end:, :]
			data_train = np.concatenate((data_train, temp), axis=0)
			data_test = bow_affective[start:end, :]
		start += step
		end += step
		bnb = MultinomialNB(alpha=0.01).fit(data_train[:, 2:], data_train[:, 0])
		lr = linear_model.LogisticRegression(solver='liblinear', n_jobs=3).fit(data_train[:, 2:], data_train[:, 0])
		total_test = 0
		true_number = 0
		true_nb = 0
		true_lr = 0
		prediction_nb = []
		prediction_lr = []
		prediction = []
		for item in data_test:
			score_table = np.zeros([2, 3], dtype=int)
			if str(item[1]) != '0':
				print item[1]
				total_test += 1
				# ENSEMBLE
				result_nb = bnb.predict([item[2:]])
				result_lr = lr.predict([item[2:]])
				result_kb = kb.predict(item[1], tt, wna, cursor, 'affective')				
				score_table[1][result_nb] += 1 
				score_table[1][result_lr] += 1 
				if result_kb != 0: 
					score_table[1][result_kb] += 1
				predicted = np.unravel_index(np.argmax(score_table, axis=None), score_table.shape)
				final_prediction = predicted[1]
				if score_table[1][predicted[1]] == 1: 
					final_prediction = result_lr 
				if final_prediction == item[0]: 
					true_number += 1
				prediction.append(int(final_prediction))

				# SINGLE
				if result_nb == item[0]:
					true_nb += 1
				if result_lr == item[0]:
					true_lr += 1
				prediction_nb.append(int(result_nb))
				prediction_lr.append(int(result_lr))
		prediction = np.array(prediction)
		prediction_nb = np.array(prediction_nb)
		prediction_lr = np.array(prediction_lr)
		if i == 9:
			nb_score = prf(data_test[:116,0], prediction_nb, average='binary')
			lr_score = prf(data_test[:116,0], prediction_lr, average='binary')
			all_score = prf(data_test[:116,0], prediction, average='binary')
		else:
			nb_score = prf(data_test[:,0], prediction_nb, average='binary')
			lr_score = prf(data_test[:,0], prediction_lr, average='binary')
			all_score = prf(data_test[:,0], prediction, average='binary')
		with open('ensemble_result[affective].txt', 'a') as file:
			file.write("\n\n\nTrue :: "+str(true_number))
			file.write(" from :: "+str(total_test))
			file.write("\nAccuracy :: "+str((float(true_number) / float(total_test))))
			file.write("\nPrecision :: "+str(all_score[0]))
			file.write("\nF-Score :: "+str(all_score[2]))

			file.write("\nNB True :: "+str(true_nb))
			file.write(" from :: "+str(total_test))
			file.write("\nAccuracy :: "+str((float(true_nb) / float(total_test))))
			file.write("\nPrecision :: "+str(nb_score[0]))
			file.write("\nF-Score :: "+str(nb_score[2]))

			file.write("\nLR True :: "+str(true_lr))
			file.write(" from :: "+str(total_test))
			file.write("\nAccuracy :: "+str((float(true_lr) / float(total_test))))
			file.write("\nPrecision :: "+str(lr_score[0]))
			file.write("\nF-Score :: "+str(lr_score[2]))
	
	bow_mixed, words_num = processWords('mixed')
	start = 0
	step = 840
	end = start + step
	tt = TreeTagger(TAGLANG='en')
	wna = WNAffect(prefix+'wordnet1.6/', prefix+'wordnetAffect/')
	for i in range(0, 10):
		if i == 0:
			data_train = bow_mixed[step:, :]
			data_test = bow_mixed[:end, :]
		elif i == 9:
			data_train = bow_mixed[:start, :]
			data_test = bow_mixed[start:, :]
		else:
			temp = bow_mixed[:start, :]
			data_train = bow_mixed[end:, :]
			data_train = np.concatenate((data_train, temp), axis=0)
			data_test = bow_mixed[start:end, :]
		start += step
		end += step
		bnb = MultinomialNB(alpha=0.01).fit(data_train[:, 2:], data_train[:, 0])
		lr = linear_model.LogisticRegression(solver='liblinear', n_jobs=3).fit(data_train[:, 2:], data_train[:, 0])
		total_test = 0
		true_number = 0
		true_nb = 0
		true_lr = 0
		prediction_nb = []
		prediction_lr = []
		prediction = []
		for item in data_test:
			score_table = np.zeros([2, 3], dtype=int)
			if str(item[1]) != '0':
				print item[1]
				total_test += 1
				# ENSEMBLE
				result_nb = bnb.predict([item[2:]])
				result_lr = lr.predict([item[2:]])
				result_kb = kb.predict(item[1], tt, wna, cursor, 'mixed')				
				score_table[1][result_nb] += 1 
				score_table[1][result_lr] += 1 
				if result_kb != 0: 
					score_table[1][result_kb] += 1
				predicted = np.unravel_index(np.argmax(score_table, axis=None), score_table.shape)
				final_prediction = predicted[1]
				if score_table[1][predicted[1]] == 1: 
					final_prediction = result_lr 
				if final_prediction == item[0]: 
					true_number += 1
		
				# SINGLE
				if result_nb == item[0]:
					true_nb += 1
				if result_lr == item[0]:
					true_lr += 1
				prediction_nb.append(int(result_nb))
				prediction_lr.append(int(result_lr))
				prediction.append(int(final_prediction))
		prediction = np.array(prediction)
		prediction_nb = np.array(prediction_nb)
		prediction_lr = np.array(prediction_lr)
		if i == 9:
			nb_score = prf(data_test[:1169,0], prediction_nb, average='binary')
			lr_score = prf(data_test[:1169,0], prediction_lr, average='binary')
			all_score = prf(data_test[:1169,0], prediction, average='binary')
		else:
			nb_score = prf(data_test[:,0], prediction_nb, average='binary')
			lr_score = prf(data_test[:,0], prediction_lr, average='binary')
			all_score = prf(data_test[:,0], prediction, average='binary')
		with open('ensemble_result[mixed].txt', 'a') as file:
			file.write("\n\n\nTrue :: "+str(true_number))
			file.write(" from :: "+str(total_test))
			file.write("\nAccuracy :: "+str((float(true_number) / float(total_test))))
			file.write("\nPrecision :: "+str(all_score[0]))
			file.write("\nF-Score :: "+str(all_score[2]))

			file.write("\nNB True :: "+str(true_nb))
			file.write(" from :: "+str(total_test))
			file.write("\nAccuracy :: "+str((float(true_nb) / float(total_test))))
			file.write("\nPrecision :: "+str(nb_score[0]))
			file.write("\nF-Score :: "+str(nb_score[2]))

			file.write("\nLR True :: "+str(true_lr))
			file.write(" from :: "+str(total_test))
			file.write("\nAccuracy :: "+str((float(true_lr) / float(total_test))))
			file.write("\nPrecision :: "+str(lr_score[0]))
			file.write("\nF-Score :: "+str(lr_score[2]))
	cursor.close()
	conn.close()
	return