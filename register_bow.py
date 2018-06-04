from mysql.connector import MySQLConnection, Error
from nltk.tokenize import word_tokenize
from python_mysql_dbconfig import read_db_config
from progress.bar import FillingSquaresBar as fsb

def registerBow():
	try:
		dbconfig = read_db_config()
		conn = MySQLConnection(**dbconfig)
		cursor = conn.cursor(buffered=True)
		# CLEAN AND RESET TABLE ID
		cursor.execute("TRUNCATE dictionary_maxentropy")
		cursor.execute("ALTER TABLE dictionary_maxentropy AUTO_INCREMENT=1")
		cursor.execute("SELECT sentence FROM preprocessed_data")
		corpus = cursor.fetchall()
		word_list = []
		pb = fsb("Registering Bow ", max=len(corpus))
		for item in corpus:
			words = word_tokenize(item[0])
			for w in words:
				if w not in word_list:
					word_list.append(w)
					# print(w)
					cursor.execute("INSERT INTO dictionary_maxentropy (word) VALUE(%(myword)s)", {'myword': w })
			pb.next()
		pb.finish()

		# Counting IDF
		# numDocuments = len(corpus)
		# cursor.execute("SELECT * from dictionary_maxentropy")
		# words = cursor.fetchall()
		# pb2 = fsb("Counting IDF ", max=len(words))
		# # print len(words)
		# for item in words:
		# 	term_count = 0
		# 	#Check on each documents
		# 	for document in corpus:
		# 		sentence = word_tokenize(document[0])
		# 		if item[1] in sentence:
		# 			term_count += 1
		# 	idf_score = log(numDocuments * term_count)
		# 	cursor.execute("UPDATE dictionary_maxentropy SET idf = %(idf)s WHERE id = %(id)s", {'idf': idf_score, 'id': item[0]})
		# 	pb2.next()
		# pb2.finish()
	except Exception as e:
		print(e)
	finally:
		conn.commit()
		cursor.close()
		conn.close()