from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config


def process_words():
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor(buffered=True)
        classes = ['joy', 'fear', 'anger', 'sadness', 'disgust', 'shame']
        i = 0
        class_count = [0, 0, 0, 0, 0, 0]
        for target in classes:
            text_list = []
            cursor.execute("SELECT Field1,SIT FROM data2 WHERE Field1=%(mytarget)s and id < 7001", {'mytarget': target})
            result = cursor.fetchall()
            for res in result:
                words = res[1].split(' ')
                for word in words:
                    print(word)
                    if word not in text_list:
                        text_list.append(word)
                    # break
                # break
            class_count[i] = len(text_list)
            i += 1
        print(class_count)
            # break
    except Error as e:
        print(e)

    finally:
        conn.commit()
        cursor.close()
        conn.close()

if __name__ == '__main__':
    process_words()