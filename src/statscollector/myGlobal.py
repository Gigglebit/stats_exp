import threading
class myGlobal(object):
	idx = 0
	tclock = threading.Lock()
