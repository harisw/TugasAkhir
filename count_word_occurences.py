from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
from progress.spinner import PieSpinner

def count_word_occurences(start, end):
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor(buffered=True)
        cursor.execute("TRUNCATE dictionary")
        classes = [1, 2, 3, 4, 5, 6]
        # classes = ['joy', 'fear', 'anger', 'sadness', 'disgust', 'shame']
        spinner = PieSpinner('\nCounting Word Occurences :: ')
        for target in classes:
            # cursor.execute("SELECT Field1,SIT FROM data2 WHERE Field1=%(mytarget)s and id < 7001", {'mytarget': target})

            if start == 1:
                cursor.execute("SELECT class, sentence FROM data3 WHERE class=%(target)s and id > %(id_target)s", {'target': target, 'id_target': end})
            elif end == 7433:
                cursor.execute("SELECT class, sentence FROM data3 WHERE class=%(target)s and id < %(id_target)s", {'target': target, 'id_target': start})
            else:              
                cursor.execute("SELECT class, sentence FROM data3 WHERE class=%(target)s and (id < %(id_start)s or id > %(id_end)s)", {'target': target,\
                 'id_start': start, 'id_end': end})
            class_documents = cursor.fetchall()
            # print(class_documents)
            for row in class_documents:
                # print(row[1])
                check = False
                sentence = row[1].split(' ')
                # print(sentence)
                # checked_sentence = []
                for word in sentence:
                    # print(word)
                    spinner.next()
                    if len(word) > 0:
                        # if word not in checked_sentence:
                            # checked_sentence.append(word)
                        # print("masuk")
                        if row[0] == 'joy':
                            cursor.execute("SELECT word, joy_occurences from dictionary WHERE word=%(target)s", {'target':word})
                        elif row[0] == 'fear':
                            cursor.execute("SELECT word, fear_occurences from dictionary WHERE word=%(target)s", {'target':word})
                        elif row[0] == 'anger':
                            cursor.execute("SELECT word, anger_occurences from dictionary WHERE word=%(target)s", {'target':word})
                        elif row[0] == 'sadness':
                            cursor.execute("SELECT word, sadness_occurences from dictionary WHERE word=%(target)s", {'target':word})
                        elif row[0] == 'disgust':
                            cursor.execute("SELECT word, disgust_occurences from dictionary WHERE word=%(target)s", {'target':word})
                        elif row[0] == 'shame':
                            cursor.execute("SELECT word, shame_occurences from dictionary WHERE word=%(target)s", {'target':word})
                        elif row[0] == 'guilt':
                            cursor.execute("SELECT word, guilt_occurences from dictionary WHERE word=%(target)s", {'target':word})
                        # print(word)

                        check_word = cursor.fetchone()
                        # print(cursor.rowcount)
                        if cursor.rowcount >= 1:
                            # print(cursor.rowcount)
                            result = check_word[1] + 1
                            if row[0] == 'joy':
                                cursor.execute("UPDATE dictionary SET joy_occurences=%(number)s WHERE word=%(target)s", {'number':result, 'target':word})
                                # cursor.execute("SELECT word, joy_occurences from dictionary WHERE word=%(target)s", {'target':word})
                            elif row[0] == 'fear':
                                cursor.execute("UPDATE dictionary SET fear_occurences=%(number)s WHERE word=%(target)s", {'number':result, 'target':word})

                                # cursor.execute("SELECT word, fear_occurences from dictionary WHERE word=%(target)s", {'target':word})
                            elif row[0] == 'anger':
                                cursor.execute("UPDATE dictionary SET anger_occurences=%(number)s WHERE word=%(target)s", {'number':result, 'target':word})
                                # cursor.execute("SELECT word, anger_occurences from dictionary WHERE word=%(target)s", {'target':word})
                            elif row[0] == 'sadness':
                                cursor.execute("UPDATE dictionary SET sadness_occurences=%(number)s WHERE word=%(target)s", {'number':result, 'target':word})
                                # cursor.execute("SELECT word, sadness_occurences from dictionary WHERE word=%(target)s", {'target':word})
                            elif row[0] == 'disgust':
                                cursor.execute("UPDATE dictionary SET disgust_occurences=%(number)s WHERE word=%(target)s", {'number':result, 'target':word})
                                # cursor.execute("SELECT word, disgust_occurences from dictionary WHERE word=%(target)s", {'target':word})
                            elif row[0] == 'shame':
                                cursor.execute("UPDATE dictionary SET shame_occurences=%(number)s WHERE word=%(target)s", {'number':result, 'target':word})
                                # cursor.execute("SELECT word, shame_occurences from dictionary WHERE word=%(target)s", {'target':word})
                            elif row[0] == 'guilt':
                                cursor.execute("UPDATE dictionary SET guilt_occurences=%(number)s WHERE word=%(target)s", {'number':result, 'target':word})
                                # cursor.execute("SELECT word, guilt_occurences from dictionary WHERE word=%(target)s", {'target':word})
                        else:
                            if row[0] == 'joy':
                                cursor.execute("INSERT INTO dictionary(word, joy_occurences) VALUES(%(target)s, 1)", {'target':word})
                            elif row[0] == 'anger':
                                cursor.execute("INSERT INTO dictionary(word, anger_occurences) VALUES(%(target)s, 1)", {'target':word})
                            elif row[0] == 'fear':
                                cursor.execute("INSERT INTO dictionary(word, fear_occurences) VALUES(%(target)s, 1)", {'target':word})
                            elif row[0] == 'sadness':
                                cursor.execute("INSERT INTO dictionary(word, sadness_occurences) VALUES(%(target)s, 1)", {'target':word})
                            elif row[0] == 'disgust':
                                cursor.execute("INSERT INTO dictionary(word, disgust_occurences) VALUES(%(target)s, 1)", {'target':word})
                            elif row[0] == 'shame':
                                cursor.execute("INSERT INTO dictionary(word, shame_occurences) VALUES(%(target)s, 1)", {'target':word})
                            elif row[0] == 'guilt':
                                cursor.execute("INSERT INTO dictionary(word, guilt_occurences) VALUES(%(target)s, 1)", {'target':word})
    except Error as e:
        print(e)

    finally:
        conn.commit()
        cursor.close()
        conn.close()
        spinner.finish()
        return 1

# if __name__ == '__main__':
#     process_words()