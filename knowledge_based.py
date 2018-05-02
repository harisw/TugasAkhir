from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
from treetagger import TreeTagger
from unidecode import unidecode
from pprint import pprint

def process_with_fetch():
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        cursor.execute("SELECT SIT FROM data_original WHERE id=289")
        row = cursor.fetchone()
        tt = TreeTagger(language='english')
        row = row[0]
        sentence = unidecode(u"When I am alone in a room with no contact with anyone - a loneliness draines me.")
        print(sentence)
        sentence = tt.tag(sentence)
        pprint(sentence)

    except Error as e:
        print(e)

    finally:
        conn.commit()
        cursor.close()
        conn.close()

if __name__ == '__main__':
	process_with_fetch()