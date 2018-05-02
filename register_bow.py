from mysql.connector import MySQLConnection, Error
from nltk.tokenize import word_tokenize
from python_mysql_dbconfig import read_db_config

def process_words():
	try:
		dbconfig = read_db_config()
		conn = MySQLConnection(**dbconfig)
		cursor = conn.cursor(buffered=True)
		cursor.execute("SELECT sentence FROM data3 where id < 20")
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

if __name__ == '__main__':
	process_words()