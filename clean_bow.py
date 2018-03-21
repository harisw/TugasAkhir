from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config

def count_probs():
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(dbconfig)
        cursor = conn.cursor(buffered=True)
        

    except expression as identifier:
        pass
    finally:
        pass

if __name__ == '__main__':
