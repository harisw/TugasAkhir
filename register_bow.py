from mysql.connector import MySQLConnection, Error
from nltk.tokenize import word_tokenize
from python_mysql_dbconfig import read_db_config

def registerBow():
	try:
		dbconfig = read_db_config()
		conn = MySQLConnection(**dbconfig)
		cursor = conn.cursor(buffered=True)

		# CLEAN AND RESET TABLE ID
		cursor.execute("TRUNCATE dictionary_maxentropy")
		cursor.execute("ALTER TABLE dictionary_maxentropy AUTO_INCREMENT=1")
		cursor.execute("SELECT sentence FROM preprocessed_data")
		
		rows = cursor.fetchall()
		word_list = []
		for item in rows:
			words = word_tokenize(item[0])
			for w in words:
				if w not in word_list:
					word_list.append(w)
					print(w)
					cursor.execute("INSERT INTO dictionary_maxentropy (word) VALUE(%(myword)s)", {'myword': w })
	except Exception as e:
		print(e)
	finally:
		conn.commit()
		cursor.close()
		conn.close()