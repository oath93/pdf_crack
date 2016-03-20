import threading
import itertools


#Uses a queue called pwd_queue. MUST BE DEFINED!!!
class GenPwds(threading.Thread):
    def __init__(self, min_spaces, max_spaces):
        self.min_spaces = min_spaces
        self.max_spaces = max_spaces

    def run(self):
        global symbols
        for i in range(self.min_spaces, self.max_spaces):
            print("Generating " + str(i) + " character passwords.")
            for combination in itertools.product(symbols, repeat=i):
                gen_pwd = (''.join(map(str, combination)))
                pwd_queue.put(gen_pwd)