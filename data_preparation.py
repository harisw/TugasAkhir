import xml.etree.ElementTree as ET
from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config

def prepareAffectiveText():
    try:
		dbconfig = read_db_config()
		conn = MySQLConnection(**dbconfig)
		cursor = conn.cursor()
		cursor.execute("TRUNCATE affective_text_original")
		
		with open('database/AffectiveText/affectivetext_trial.emotions.gold') as file:
			emo_xml = file.readlines()
		trial_count = len(emo_xml)
		with open('database/AffectiveText/affectivetext_test.emotions.gold') as file:
			emo_test_xml = file.readlines()

		parser = ET.XMLParser(encoding="utf-8")
		elem_trial = ET.parse('database/AffectiveText/affectivetext_trial.xml')
		elem_test = ET.parse('database/AffectiveText/affectivetext_test.xml', parser=parser)
		elem = elem_trial
		emo_xml = emo_xml[1:]
		processSentence(emo_xml, elem_trial, cursor)
		processSentence(emo_test_xml, elem_test, cursor)
    except Error as e:
		print(e)

    finally:
		conn.commit()
		cursor.close()
		conn.close()

def processSentence(emo_xml, elem, cursor):
	for item in emo_xml:
		emotion_scores = str(item).split(' ')
		print emotion_scores[0]
		scores = []
		scores.append([int(emotion_scores[1]), 'anger'])
		scores.append([int(emotion_scores[2]), 'disgust'])
		scores.append([int(emotion_scores[3]), 'fear'])
		scores.append([int(emotion_scores[4]), 'joy'])
		scores.append([int(emotion_scores[5]), 'sadness'])
		max_emotion = 0
		current_class = ''

		for emotion in scores:
			if emotion[0] > max_emotion:
				max_emotion = emotion[0]
				current_class = emotion[1]
		if current_class != '':
			current_sentence = elem.find('.//instance[@id="'+emotion_scores[0]+'"]').text
			cursor.execute("INSERT INTO affective_text_original(class, sentence) VALUES(%s, %s) ", (current_class, current_sentence))
	return