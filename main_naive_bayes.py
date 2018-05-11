from count_class_word import count_class_word
from count_word_occurences import count_word_occurences
from count_probs import count_probs
from testing_naivebayes import test_naive_bayes

if __name__ == '__main__':
	step_constant = 694
	initial = 1
	start = 1
	end = 694
	while(initial <= 1):
		count_class_word(start, end)
		count_word_occurences(start, end)
		count_probs()
		test_naive_bayes(start, end)
		start += step_constant
		end += step_constant
		initial += 1
	print "\n\nDONE"