from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
import operator
from progress.spinner import PieSpinner

def test_naive_bayes(start, end):
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor(buffered=True)

        cursor.execute("select count(id) as total from data3 group by class")
        total_class = cursor.fetchall()
        print(total_class)
        joy = float(total_class[0][0])
        fear = float(total_class[0][0])
        anger = float(total_class[0][0])
        disgust = float(total_class[0][0])
        sad = float(total_class[0][0])
        shame = float(total_class[0][0])
    
        cursor.execute("SELECT words FROM meta_class");
        class_word = cursor.fetchall()
        word_each_class = [class_word[0][0], class_word[1][0], class_word[2][0], class_word[3][0], class_word[4][0], class_word[5][0]]

        # class_list = [classes[0].split(' ')[0], classes[1].split(' ')[0], classes[2].split(' ')[0], \
                        # classes[3].split(' ')[0], classes[4].split(' ')[0], classes[5].split(' ')[0]]
        class_list = [1, 2, 3, 4, 5, 6] 
        if start == 1:
            cursor.execute("SELECT * FROM data3 WHERE id <= %(id_target)s", {'id_target': end})
        elif end == 7433:
            cursor.execute("SELECT * FROM data3 WHERE id => %(id_target)s", {'id_target': start})
        else:              
            cursor.execute("SELECT * FROM data3 WHERE id >= %(id_start)s and id <= %(id_end)s", {'id_start': start, 'id_end': end})
        # cursor.execute("SELECT * FROM data WHERE id > 7600")
        results = cursor.fetchall()
        results_amount = len(results)
        # cursor.execute("SELECT COUNT(*) FROM data2 WHERE id > 7600")
        # results_amount = cursor.fetchone()
        # results_amount = results_amount[0]
        true_amount = 0
        # test_amount = 0
        print results_amount
        cursor.execute("SELECT * from data3")
        print ("start :: "+str(start))
        print ("end :: "+str(end))
        total_data = len(cursor.fetchall())
        print total_data
        total_data = total_data - results_amount
        # print total_data
        joy_prior_probs = joy / total_data
        fear_prior_probs = fear / total_data
        anger_prior_probs = anger / total_data
        sadness_prior_probs = sad / total_data
        disgust_prior_probs = disgust / total_data
        shame_prior_probs = shame / total_data
        pie = PieSpinner('\nTesting Naive Bayes :: ')
        for res in results:

            pie.next()
            sentence = res[2].split(' ')
            
            joy_x = 1
            fear_x = 1
            anger_x = 1
            sadness_x = 1
            disgust_x = 1
            shame_x = 1
            check = False

            # checked_sentence = []
            # print(sentence[0])
            for word in sentence:
                # print(word)
                if word != " ":
                    check = True
                if check and len(word) > 2:
                    # print("hitung")
                    # checked_sentence.append(word)
                    cursor.execute("SELECT joy_probs from dictionary WHERE word=%(target)s", {'target': word})
                    probs_res = cursor.fetchone()
                    if(cursor.rowcount > 0 and probs_res[0] >0):
                        # print(probs_res[0])
                        joy_x = joy_x*probs_res[0]
                    else:
                        joy_x = joy_x *(float(1)/float(word_each_class[0]))

                    cursor.execute("SELECT fear_probs from dictionary where word=%(target)s", {'target': word})
                    probs_res = cursor.fetchone()
                    if(cursor.rowcount > 0 and probs_res[0] >0):
                        fear_x = fear_x*probs_res[0]
                    else:
                        fear_x = fear_x *(float(1)/float(word_each_class[1]))

                    cursor.execute("SELECT anger_probs from dictionary where word=%(target)s", {'target': word})
                    probs_res = cursor.fetchone()
                    if(cursor.rowcount > 0 and probs_res[0] >0):
                        anger_x = anger_x*probs_res[0]
                    else:
                        anger_x = anger_x *(float(1)/float(word_each_class[2]))

                    cursor.execute("SELECT sadness_probs from dictionary WHERE word=%(target)s", {'target': word})
                    probs_res = cursor.fetchone()
                    if(cursor.rowcount > 0 and probs_res[0] >0):
                        sadness_x = sadness_x*probs_res[0]
                    else:
                        sadness_x = sadness_x *(float(1)/float(word_each_class[3]))

                    cursor.execute("SELECT disgust_probs from dictionary WHERE word=%(target)s", {'target': word})
                    probs_res = cursor.fetchone()
                    if(cursor.rowcount > 0 and probs_res[0] >0):
                        disgust_x = disgust_x*probs_res[0]
                    else:
                        disgust_x = disgust_x *(float(1)/float(word_each_class[4]))

                    cursor.execute("SELECT shame_probs from dictionary WHERE word=%(target)s", {'target': word})
                    probs_res = cursor.fetchone()
                    if(cursor.rowcount > 0 and probs_res[0] >0):
                        shame_x = shame_x*probs_res[0]
                    else:
                        shame_x = shame_x *(float(1)/float(word_each_class[5]))
                # break
                check = True

            joy_probs = float(joy_x) * joy_prior_probs * 1000000000
            fear_probs = float(fear_x) * fear_prior_probs * 1000000000
            anger_probs = float(anger_x) * anger_prior_probs * 1000000000
            sadness_probs = float(sadness_x) * sadness_prior_probs * 1000000000
            disgust_probs = float(disgust_x) * disgust_prior_probs * 1000000000
            shame_probs = float(shame_x) * shame_prior_probs * 1000000000
            
            # probs_list = {1: joy_probs, 2: fear_probs, 3: anger_probs, 4: sadness_probs, 5: disgust_probs, 6: shame_probs, 7: guilt_probs}
            # print(probs_list[6])
            # probs_list = sorted(probs_list.items(), key=operator.itemgetter(1))
            # print(probs_list)
            
            probs_list = [joy_probs, fear_probs, anger_probs, disgust_probs, sadness_probs, shame_probs]
            print("\nJoy    : {0:.35f},\nFear   : {1:.35f}, \nAnger  : {2:.35f}, \nDisgust: {3:.35f}, \nSad    : {4:.35f}, \nShame  : {5:.35f}" \
                    .format(joy_probs, fear_probs, anger_probs, disgust_probs, sadness_probs, shame_probs))
            prediction = find_max(probs_list)
            # print(prediction)
            # print("Real Class: %s " % res[1])
            # print("Prediction: %s " % class_list[prediction])
            print res[1]
            print class_list[prediction]
            print prediction
            if res[1] == class_list[prediction]:
                true_amount += 1
            break
        accuracy = (float(true_amount) / float(results_amount)) * 100
        print("Accuracy : {0:.4f}".format(accuracy))
        # print(true_amount)
        # print(results_amount)
        pie.finish()
    except Error as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

def find_max(prob_list):
    my_max = prob_list[0]
    max_index = 0
    curr_index = 0
    for item in prob_list:
        if item > my_max:
            my_max = item
            max_index = curr_index
        curr_index += 1
    return max_index

# if __name__ == '__main__':
#     test_naive_bayes()