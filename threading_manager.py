import threading
from time import sleep


class ThreadManager(threading.Thread):
    def __init__(self, max_threads = 1):
        super(ThreadManager, self).__init__()
        self.max_threads = max_threads
        self.threads = []
        self.cleaning = True
        self.exc_info = None
        self.cleaner_thread = None

    def add_thread(self, new_thread, to_run = None):
        if len(self.threads) < self.max_threads:
            if to_run == None:
                new_thread.start()
            else:
                new_thread.run(to_run)
            self.threads.append(new_thread)
            return True
        return False


    def cleaner(self):
        if len(self.threads) == self.max_threads - 1:
            print("-" * 40)
            print("Found threads to be max.")
            print("-" * 40)
        while self.cleaning:
            for thread in range(len(self.threads)):
                if not thread > len(self.threads) - 1:
                    if not self.threads[thread].is_alive():
                        if self.threads[thread].exc_info:
                            self.cleaning = False
                            self.exc_info = self.threads[thread].exc_info
                            return self.exc_info
                        self.threads.pop(thread)

    def run(self):
        if self.cleaner_thread == None:
            self.cleaner_thread = threading._start_new_thread(self.cleaner, ())
        while self.cleaning:
            if self.exc_info:
                raise

class MasterThread(threading.Thread):
    def __init__(self, manager):
        super(MasterThread, self).__init__()
        self.manager = manager

    def change_max_threads(self, new_max):
        print("Active Threads: " + str(self.manager.max_threads))
        if not self.manager.max_threads == new_max:
            self.manager.max_threads = new_max
            self.manager.cleaning = False
            self.manager.cleaner_thread = None

            print("Changed active threads to " + str(new_max))
    def run(self):
        self.manager.start()
        while True:
            if not self.manager.is_alive():
                self.manager = ThreadManager(self.manager.max_threads)
                self.manager.cleaning = True
                self.manager.start()



class ThreadInfo:
    def __init__(self, threads, prev_pass_per_min = 0):
        self.threads = threads
        self.best_threads = 0
        self.pppm = prev_pass_per_min
        self.checks_since_change = 0
        self.best_pass_per_min = 0
        self.fresh = True
        self.decreased_last = False

    def change_threads(self, pass_per_min, increased_last):
        if self.checks_since_change > 5 and pass_per_min < self.best_pass_per_min:
            to_return = False
            if not increased_last:
                self.threads +=1
                self.decreased_last = False
                self.checks_since_change = 0
                self.pppm = pass_per_min
                to_return = True
            else:
                self.threads -=1
                self.decreased_last = True
                self.checks_since_change = 0
            if pass_per_min > self.best_pass_per_min:
                self.best_pass_per_min = pass_per_min
                self.best_threads = self.threads
            return to_return

        if pass_per_min > self.best_pass_per_min:
            self.best_pass_per_min = pass_per_min
            self.best_threads = self.threads
        if self.fresh: #still a new object
            self.threads += 1
            self.decreased_last = False
            self.checks_since_change = 0
            self.fresh = False
            return True
        if pass_per_min > self.pppm and increased_last:
            self.threads += 1
            self.checks_since_change = 0
            self.pppm = pass_per_min
            self.decreased_last = False
            return True
        elif pass_per_min > self.pppm and self.decreased_last:
            self.threads -=1
            self.checks_since_change = 0
            self.pppm = pass_per_min
            self.decreased_last = True
            return False
        if pass_per_min < self.pppm and increased_last:
            self.threads -=1
            self.checks_since_change = 0
            self.decreased_last = True
            self.pppm = pass_per_min
            return False
        if pass_per_min < self.pppm and self.decreased_last:
            self.threads +=1
            self.decreased_last = False
            self.checks_since_change = 0
            self.pppm = pass_per_min
            return True
        if self.decreased_last == increased_last and pass_per_min < self.best_pass_per_min:
            if self.threads < self.best_threads:
                self.threads +=1
                self.decreased_last = False
                self.checks_since_change = 0
                self.pppm = pass_per_min
                return True
            if self.threads > self.best_threads:
                self.threads -=1
                self.checks_since_change = 0
                self.decreased_last = True
                self.pppm = pass_per_min
                return False

        self.checks_since_change +=1
        return False




