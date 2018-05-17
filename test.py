from os import listdir

def see(path='.'):
	for i in listdir(path):
		yield i

for i in see():
	print i