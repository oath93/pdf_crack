import threading
import PyPDF2

class ThreadPwd(threading.Thread):

    def __init__(self, pwd, pdf):
        super(ThreadPwd, self).__init__()
        self.pwd = pwd
        self.pdf = pdf
        self.exc_info = None

    def set_thread(self, pwd, pdf):
        self.pdf = pdf
        self.pwd = pwd

    def run(self):
        log_file = open('pwd_thread_log.txt', 'w')
        if self.pwd == None:
            raise ValueError("No password to check")
        while True:
            try:
                log_file.write("attempted " + self.pwd + '\n')
                decrypt_result = self.pdf.decrypt(self.pwd)
                break
            except PyPDF2.utils.PdfReadError:
                print("Pdf Decrypt PdfReadError Occured. Retrying.")
            except ValueError:
                print("Pdf Decrypt ValuError Occured. Retrying.")
        if decrypt_result > 0:
            log_file.write("Found pwd of " + self.pwd)
            log_file.close()
            try:
                raise FoundPwd(self.pwd)
            except FoundPwd:
                import sys
                self.exc_info = sys.exc_info()
        if self.exc_info:
            return self.exc_info


class FoundPwd(Exception):
    def __init__(self, pwd):
        self.pwd = pwd