from progress.spinner import PieSpinner
import time

spinner = PieSpinner("Doing some Work  ")
i = 50
while i > 0:
	i -= 1
	spinner.next()
	time.sleep(0.1)

spinner.finish()