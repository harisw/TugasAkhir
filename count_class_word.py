from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
from progress.spinner import PieSpinner

def count_class_word(start, end):
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor(buffered=True)
        cursor.execute("TRUNCATE meta_class")
        # classes = ['joy', 'fear', 'anger', 'sadness', 'disgust', 'shame']
        classes = [1, 2, 3, 4, 5, 6]
        i = 1
        class_count = [0, 0, 0, 0, 0, 0, 0]
        spinner = PieSpinner('\nCounting Class Word ::  ')
        for target in classes:
            text_list = []
            # cursor.execute("SELECT class,SIT FROM data3 WHERE class=%(mytarget)s and id < 7001", {'mytarget': target})
            if start == 1:
                cursor.execute("SELECT class, sentence FROM data3 WHERE class=%(target)s and id > %(id_target)s", {'target': target, 'id_target': end})
            elif end == 7433:
                cursor.execute("SELECT class, sentence FROM data3 WHERE class=%(target)s and id < %(id_target)s", {'target': target, 'id_target': start})
            else:              
                cursor.execute("SELECT class, sentence FROM data3 WHERE class=%(target)s and (id < %(id_start)s or id > %(id_end)s)", {'target': target,\
                 'id_start': start, 'id_end': end})

            result = cursor.fetchall()
            for res in result:
                words = res[1].split(' ')
                for word in words:
                    if word not in text_list and len(word) > 0:
                        # print(word)
                        text_list.append(word)
                    spinner.next()
            class_count[i] = len(text_list)
            cursor.execute("INSERT INTO meta_class values(%(id)s, %(class)s, %(word)s)", {'id': i, 'class':classes[i-1], 'word':len(text_list)})
            i += 1
        spinner.finish()
        # print(class_count)
            # break
    except Error as e:
        print(e)

    finally:
        conn.commit()
        cursor.close()
        conn.close()
        return 1

# if __name__ == '__main__':
#     process_words()