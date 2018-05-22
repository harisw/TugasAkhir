from Preprocess_bow import preprocess
import train_maxentropy as tm
from register_bow import registerBow

if __name__ == '__main__':
	preprocess()
	registerBow()
	tm.classifying()