from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
import operator

def test_naive_bayes():
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor(buffered=True)

        file = open("constant.txt", "r+")
        classes = file.read()
        classes = classes.splitlines()

        joy = float(classes[0].split(' ')[1])
        fear = float(classes[1].split(' ')[1])
        anger = float(classes[2].split(' ')[1])
        disgust = float(classes[3].split(' ')[1])
        sad = float(classes[4].split(' ')[1])
        shame = float(classes[5].split(' ')[1])
    
        cursor.execute("SELECT words FROM meta_class");
        class_word = cursor.fetchall()
        word_each_class = [class_word[0][0], class_word[1][0], class_word[2][0], class_word[3][0], class_word[4][0], class_word[5][0]]

        class_list = [classes[0].split(' ')[0], classes[1].split(' ')[0], classes[2].split(' ')[0], \
                        classes[3].split(' ')[0], classes[4].split(' ')[0], classes[5].split(' ')[0]]
        
        cursor.execute("SELECT * FROM data2 WHERE id>=7001")
        results = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) FROM data2 WHERE id>=7001")
        results_amount = cursor.fetchone()
        results_amount = results_amount[0]
        true_amount = 0
        # test_amount = 0

        for res in results:
            sentence = res[5].split(' ')
            
            joy_prior_probs = joy / 5849
            fear_prior_probs = fear / 5849
            anger_prior_probs = anger / 5849
            sadness_prior_probs = sad / 5849
            disgust_prior_probs = disgust / 5849
            shame_prior_probs = shame / 5849
            
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
                print(word)
                if word != " ":
                    check = True
                if check and len(word) > 2:
                    print("hitung")
                    # checked_sentence.append(word)
                    cursor.execute("SELECT joy_probs from dictionary WHERE word=%(target)s", {'target': word})
                    probs_res = cursor.fetchone()
                    if(cursor.rowcount >0):
                        joy_x = joy_x*probs_res[0]
                    else:
                        joy_x = joy_x *(float(1)/float(word_each_class[0]))

                    cursor.execute("SELECT fear_probs from dictionary where word=%(target)s", {'target': word})
                    probs_res = cursor.fetchone()
                    if(cursor.rowcount >0):
                        fear_x = fear_x*probs_res[0]
                    else:
                        fear_x = fear_x *(float(1)/float(word_each_class[1]))

                    cursor.execute("SELECT anger_probs from dictionary where word=%(target)s", {'target': word})
                    probs_res = cursor.fetchone()
                    if(cursor.rowcount >0):
                        anger_x = anger_x*probs_res[0]
                    else:
                        anger_x = anger_x *(float(1)/float(word_each_class[2]))

                    cursor.execute("SELECT sadness_probs from dictionary WHERE word=%(target)s", {'target': word})
                    probs_res = cursor.fetchone()
                    if(cursor.rowcount >0):
                        sadness_x = sadness_x*probs_res[0]
                    else:
                        sadness_x = sadness_x *(float(1)/float(word_each_class[3]))

                    cursor.execute("SELECT disgust_probs from dictionary WHERE word=%(target)s", {'target': word})
                    probs_res = cursor.fetchone()
                    if(cursor.rowcount >0):
                        disgust_x = disgust_x*probs_res[0]
                    else:
                        disgust_x = disgust_x *(float(1)/float(word_each_class[4]))

                    cursor.execute("SELECT shame_probs from dictionary WHERE word=%(target)s", {'target': word})
                    probs_res = cursor.fetchone()
                    if(cursor.rowcount >0):
                        shame_x = shame_x*probs_res[0]
                    else:
                        shame_x = shame_x *(float(1)/float(word_each_class[5]))
                # break
                check = True

            joy_probs = float(joy_x) * joy_prior_probs * 10000000
            fear_probs = float(fear_x) * fear_prior_probs * 10000000
            anger_probs = float(anger_x) * anger_prior_probs * 10000000
            sadness_probs = float(sadness_x) * sadness_prior_probs * 10000000
            disgust_probs = float(disgust_x) * disgust_prior_probs * 10000000
            shame_probs = float(shame_x) * shame_prior_probs * 10000000
            
            # probs_list = {1: joy_probs, 2: fear_probs, 3: anger_probs, 4: sadness_probs, 5: disgust_probs, 6: shame_probs, 7: guilt_probs}
            # print(probs_list[6])
            # probs_list = sorted(probs_list.items(), key=operator.itemgetter(1))
            # print(probs_list)
            
            probs_list = [joy_probs, fear_probs, anger_probs, disgust_probs, sadness_probs, shame_probs]
            print("Joy    : {0:.17f},\nFear   : {1:.17f}, \nAnger  : {2:.17f}, \nDisgust: {3:.17f}, \nSad    : {4:.17f}, \nShame  : {5:.17f}" \
                    .format(joy_probs, fear_probs, anger_probs, disgust_probs, sadness_probs, shame_probs))
            prediction = find_max(probs_list)
            print(prediction)
            print("Real Class: %s " % res[1])
            print("Prediction: %s " % class_list[prediction])
            if res[1] == class_list[prediction]:
                true_amount += 1
        
        accuracy = (float(true_amount) / float(results_amount)) * 100
        print("Accuracy : {0:.4f}".format(accuracy))
        print(true_amount)
        print(results_amount)
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

if __name__ == '__main__':
    test_naive_bayes()