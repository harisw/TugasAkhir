from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
from progress.spinner import PieSpinner

def count_probs():
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor(buffered=True)
        
        cursor.execute("SELECT * FROM dictionary")
        results = cursor.fetchall()
        cursor.execute("SELECT * FROM meta_class")
        classes = cursor.fetchall()
        joy = float(classes[0][2])
        fear = float(classes[1][2])
        anger = float(classes[2][2])
        sad = float(classes[3][2])
        disgust = float(classes[4][2])
        shame = float(classes[5][2])
        spinner = PieSpinner('\nCounting Probabilities :: ')
        for res in results:
            # print(res[1])
            spinner.next()
            total_occurences = res[2] + res[3] + res[4] + res[5] + res[6] + res[7]
            # if total_occurences < 10:
                # print(res)
            joy_probs = res[2] / joy
            fear_probs = res[3] / fear
            anger_probs = res[4] / anger
            sad_probs = res[5] / sad
            disgust_probs = res[6] / disgust
            shame_probs = res[7] / shame
            cursor.execute("UPDATE dictionary SET joy_probs=%(joy)s, fear_probs=%(fear)s, anger_probs=%(anger)s, sadness_probs=%(sad)s, \
                            disgust_probs=%(disgust)s, shame_probs=%(shame)s WHERE id=%(target)s", {'joy':joy_probs, \
                            'fear': fear_probs, 'anger': anger_probs, 'sad': sad_probs, 'disgust': disgust_probs, 'shame': shame_probs, 'target': res[0]})
        # classes = ['joy', 'fear', 'anger', 'sadness', 'disgust', 'shame', 'guilt']

    except Error as e:
        print(e)
    finally:
        conn.commit()
        cursor.close()
        conn.close()
        spinner.finish()
        # return 1

# if __name__ == '__main__':
#     count_probs()