import Preprocess as pp
import train_maxentropy as tm
from register_bow import registerBow

if __name__ == '__main__':
	# pp.begin()
	tm.classifyingCV()
	# tm.classifyingAffective()
	# tm.singleClassifierAffective()