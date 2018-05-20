from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
import re
from progress.bar import FillingCirclesBar as fcb
from autocorrect import spell
from nltk.tokenize import word_tokenize

def correcting():
	try:
		dbconfig = read_db_config()
		conn = MySQLConnection(**dbconfig)
		cursor = conn.cursor(buffered=True)
		
		cursor.execute("SELECT * from cleaned_data_original")
		result = cursor.fetchall()
		sentences_list = []
		progressbar = fcb('Correcting typo ', max=len(result))
		for res in result:
			sentence = word_tokenize(res[2])
			last_string = ""
			for w in sentence:
				w = spell(w)
				last_string += w + " "
			result = cursor.execute("UPDATE cleaned_data_original set class=%s , sentence=%s WHERE id=%s", (res[1], last_string, res[0]))
			progressbar.next()
		progressbar.finish()
	except Error as e:
		print(e)
	finally:
		conn.commit()
		cursor.close()
		conn.close()

if __name__ == '__main__':
	correcting()