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
        spinner = PieSpinner("\nCounting Word Occurences ") 
        for target in classes:
            if start == 1:
                cursor.execute("SELECT class, sentence FROM data3 WHERE class=%(target)s and id > %(id_target)s", {'target': target, 'id_target': end})
            elif end == 7433:
                cursor.execute("SELECT class, sentence FROM data3 WHERE class=%(target)s and id < %(id_target)s", {'target': target, 'id_target': start})
            else:              
                cursor.execute("SELECT class, sentence FROM data3 WHERE class=%(target)s and (id < %(id_start)s or id > %(id_end)s)", {'target': target,\
                 'id_start': start, 'id_end': end})
            class_documents = cursor.fetchall()
            for row in class_documents:
                check = False
                sentence = row[1].split(' ')
                for word in sentence:
                    spinner.next()
                    if len(word) > 0:
                        if row[0] == '1':
                            cursor.execute("SELECT word, joy_occurences from dictionary WHERE word=%(target)s", {'target':word})
                        elif row[0] == '2':
                            cursor.execute("SELECT word, fear_occurences from dictionary WHERE word=%(target)s", {'target':word})
                        elif row[0] == '3':
                            cursor.execute("SELECT word, anger_occurences from dictionary WHERE word=%(target)s", {'target':word})
                        elif row[0] == '4':
                            cursor.execute("SELECT word, sadness_occurences from dictionary WHERE word=%(target)s", {'target':word})
                        elif row[0] == '5':
                            cursor.execute("SELECT word, disgust_occurences from dictionary WHERE word=%(target)s", {'target':word})
                        elif row[0] == '6':
                            cursor.execute("SELECT word, shame_occurences from dictionary WHERE word=%(target)s", {'target':word})

                        check_word = cursor.fetchone()
                        if check_word != None:
                            result = check_word[1] + 1
                            if row[0] == '1':
                                cursor.execute("UPDATE dictionary SET joy_occurences=%(number)s WHERE word=%(target)s", {'number':result, 'target':word})
                                # cursor.execute("SELECT word, joy_occurences from dictionary WHERE word=%(target)s", {'target':word})
                            elif row[0] == '2':
                                cursor.execute("UPDATE dictionary SET fear_occurences=%(number)s WHERE word=%(target)s", {'number':result, 'target':word})

                                # cursor.execute("SELECT word, fear_occurences from dictionary WHERE word=%(target)s", {'target':word})
                            elif row[0] == '3':
                                cursor.execute("UPDATE dictionary SET anger_occurences=%(number)s WHERE word=%(target)s", {'number':result, 'target':word})
                                # cursor.execute("SELECT word, anger_occurences from dictionary WHERE word=%(target)s", {'target':word})
                            elif row[0] == '4':
                                cursor.execute("UPDATE dictionary SET sadness_occurences=%(number)s WHERE word=%(target)s", {'number':result, 'target':word})
                                # cursor.execute("SELECT word, sadness_occurences from dictionary WHERE word=%(target)s", {'target':word})
                            elif row[0] == '5':
                                cursor.execute("UPDATE dictionary SET disgust_occurences=%(number)s WHERE word=%(target)s", {'number':result, 'target':word})
                                # cursor.execute("SELECT word, disgust_occurences from dictionary WHERE word=%(target)s", {'target':word})
                            elif row[0] == '6':
                                cursor.execute("UPDATE dictionary SET shame_occurences=%(number)s WHERE word=%(target)s", {'number':result, 'target':word})
                                # cursor.execute("SELECT word, shame_occurences from dictionary WHERE word=%(target)s", {'target':word})

                        else:
                            if row[0] == '1':
                                cursor.execute("INSERT INTO dictionary(word, joy_occurences) VALUES(%(target)s, 1)", {'target':word})
                            elif row[0] == '2':
                                cursor.execute("INSERT INTO dictionary(word, fear_occurences) VALUES(%(target)s, 1)", {'target':word})
                            elif row[0] == '3':
                                cursor.execute("INSERT INTO dictionary(word, anger_occurences) VALUES(%(target)s, 1)", {'target':word})                            
                            elif row[0] == '4':
                                cursor.execute("INSERT INTO dictionary(word, sadness_occurences) VALUES(%(target)s, 1)", {'target':word})
                            elif row[0] == '5':
                                cursor.execute("INSERT INTO dictionary(word, disgust_occurences) VALUES(%(target)s, 1)", {'target':word})
                            elif row[0] == '6':
                                cursor.execute("INSERT INTO dictionary(word, shame_occurences) VALUES(%(target)s, 1)", {'target':word})

    except Error as e:
        print(e)

    finally:
        conn.commit()
        cursor.close()
        conn.close()
        spinner.finish()

# if __name__ == '__main__':
#     count_word_occurences(5, 10)