from mysql.connector import MySQLConnection, Error
from nltk.tokenize import word_tokenize
from python_mysql_dbconfig import read_db_config
from sklearn import linear_model
from sklearn import metrics
from sklearn.cross_validation import train_test_split
import pandas as pd
import numpy as np

def process_words():
	try:
		dbconfig = read_db_config()
		conn = MySQLConnection(**dbconfig)
		cursor = conn.cursor(buffered=True)

		# CREATE EMPTY BOW
		cursor.execute("SELECT * FROM dictionary_maxentropy")
		rows = cursor.fetchall()
		empty_bow = pd.DataFrame()
		# empty_bow = pd.concat([pd.DataFrame([0], columns=[item[1]]) for item in rows])
		for item in rows:	#PREFER USING THIS WAY TO MAINTAIN PROGRESS TRACKING
			print(item[1])
			empty_bow[item[1]] = np.nan
			# empty_bow = empty_bow.assign(item[1]=0)
			# empty_bow = empty_bow.append({ item[1]: 0}, ignore_index=True)
		empty_bow['class'] = np.nan
		print(empty_bow.head())

		all_data = pd.DataFrame()
		#CREATE BOW VECTOR
		cursor.execute("SELECT * FROM data3 where id<20")
		rows = cursor.fetchall()
		for item in rows:
			my_bow = empty_bow
			words = word_tokenize(item[2])
			for w in words:
				cursor.execute("SELECT id from dictionary_maxentropy where word = %(target)s", {'target': w})
				res = cursor.fetchone()
				my_bow[w] += 1
			my_bow['class'] = item[1]
			# print(my_bow)
			all_data = all_data.append(my_bow)
		# print(my_bow)
		print(all_data.head())
	except Exception as e:
		print(e)
	finally:
		conn.commit()
		cursor.close()
		conn.close()

if __name__ == '__main__':
	process_words()