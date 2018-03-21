from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config

def count_probs():
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor(buffered=True)
        
        file = open("constant.txt", "r+")
        classes = file.read()
        classes = classes.splitlines()
        print(classes)
        cursor.execute("SELECT * FROM dictionary")
        results = cursor.fetchall()
        joy = float(classes[0].split(' ')[1])
        anger = float(classes[1].split(' ')[1])
        fear = float(classes[2].split(' ')[1])
        disgust = float(classes[3].split(' ')[1])
        guilt = float(classes[4].split(' ')[1])
        sad = float(classes[5].split(' ')[1])
        shame = float(classes[6].split(' ')[1])
        for res in results:
            print(res[1])
            joy_probs = res[2] / joy
            fear_probs = res[3] / fear
            anger_probs = res[4] / anger
            sad_probs = res[5] / sad
            disgust_probs = res[6] / disgust
            shame_probs = res[7] / shame
            guilt_probs = res[8] / guilt
            cursor.execute("UPDATE dictionary SET joy_probs=%(joy)s, fear_probs=%(fear)s, anger_probs=%(anger)s, sadness_probs=%(sad)s, \
                            disgust_probs=%(disgust)s, shame_probs=%(shame)s, guilt_probs=%(guilt)s WHERE id=%(target)s", {'joy':joy_probs, \
                            'fear': fear_probs, 'anger': anger_probs, 'sad': sad_probs, 'disgust': disgust_probs, 'shame': shame_probs, 'guilt': guilt_probs, 'target': res[0]})
        # classes = ['joy', 'fear', 'anger', 'sadness', 'disgust', 'shame', 'guilt']

    except Error as e:
        print(e)
    finally:
        conn.commit()
        cursor.close()
        conn.close()
        file.close()

if __name__ == '__main__':
    count_probs()