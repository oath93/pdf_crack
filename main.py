"""
Test:

Fix / Adjust:
    Fix total runtime calculation (check pwd per minute calculations)
    work on thread_info class
        aiming to have it store information about how many threads exist,
        previous pass per minute, and do smart check for
        increasing/decreasing thread counts.
        CANNOT STORE THE THREAD MANAGER
        WITHOUT INITIALIZING MANAGER WITHIN THREAD_INFO CLASS!!!!

To Add:

"""

import sys
import itertools
import thread_pwd
from threading import _start_new_thread
from threading_manager import ThreadManager, MasterThread, ThreadInfo
from timing import *
import queue

start = string_to_float(now())



##################################################
####End ThreadInfo class#########################


def all_strings(pwd):
    s = pwd.lower()
    for p in itertools.product(*[(0,1)]*len(s)):
        yield ''.join( c.upper() if t else c for t,c in zip(p,s))



while True:
    try:
        file_name = input("Enter a file name located in the same directory.")
        if not file_name[-4:] == '.pdf':
            file_name = file_name + '.pdf'
        print("Do you want to try to crack " + file_name + '?')
        uinput = input("1 = yes 0 = no \n")
        if int(uinput) == 1:
            break
    except ValueError:
        print("Invalid Input. Try again.\n")


threads = 4
min_spaces = 0
max_spaces = 0
thread_count = 0
tested = 0
prev_pass_per_min = 0
best_avg_ppm = 0
best_avg_threads = 0

increased_last = False  #if thread count was last increased or not
found_pwd = ""
found = False
pdfFile = open(file_name, 'rb')
pdf = thread_pwd.PyPDF2.PdfFileReader(pdfFile) #PyPDF2 imported in thread_pwd.py, not imported again

if not pdf.isEncrypted:
    print("The selected pdf is not encrypted. No password needed.")
    sys.exit()


alpha = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
             'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
numeric = ['0','1','2','3','4','5','6','7','8','9']
base_symbol = ['!','@','#','$','%','^','&','*','(',')','-','_']
extended_symbol = ['<','>','\'',',','.','/','?','[',']','{','}','|','+','=']
symbols = []


########################
####Choosing Symbols####
########################
options = []
while True:
    try:
        print("Choose what to add to check: ")
        print("1: Alpha characters (a, b, c, A, B, C, etc)")
        print("2: Numeric Characters (1, 2, etc)")
        print("3: Base symbols ( ! @ # $ % ^ & * ( ) - _ )")
        print("4: Extended symbols ( < > , . / ? [ ] { } | + = )")
        print("5: Full Check (options 1 - 4 )")
        print("6: Dictionary-based\n")
        choice = int(input("Enter an option: "))
    except NameError:
        print("You must enter a value!")
        continue
    except ValueError:
        print("Only input a number!")
        continue
    if choice > 6 or choice < 1:
        print("Enter a number in the menu.")
        continue

    if not choice in options:
        options.append(choice)
    if choice == 6:
        print("!"*80)
        print("!!!WARNING!!!")
        print("The inherent dictionary for this program is a list of the top 1000 passwords")
        print("in all combinations of upper and lower case. Including this list will add 140,576")
        print("combinations to each level of password check, which can greatly increase your time")
        print("to crack a password that is NOT based on a dictionary word.")
        uinput = input("If you still want to add this, type 'yes' or 'Yes'. Otherwise, this option will not be added." )
        if uinput == 'yes' or 'Yes':
            break
        options.pop(-1)
    print()
    try:
        cont = int(input("Pick another? (1 = yes, 0 = no)"))
    except:
        print("You did something wrong...")
        continue
    if cont == 0:
        break

options.sort()
options.reverse()
for choice in options:
    if choice == 6:
        try:
            pwd_file = open('passwords','r')
            large_pwd = pwd_file.read()
            top_pwd = large_pwd.splitlines()
            pwd_file.close()
        except FileNotFoundError:
            print("There was no passwords file found!")

    if choice == 5:
        symbols = alpha + numeric + base_symbol + extended_symbol
        break  #No need to keep looking, all available options are present

    if choice == 1:
        symbols = symbols + alpha

    if choice == 2:
        symbols = symbols + numeric

    if choice == 3:
        symbols = symbols + base_symbol

    if choice == 4:
        symbols = symbols + extended_symbol

#####################Finished with symbols to check######################
#########################################################################


while True:
    try:
        min_spaces = int(input("Enter the minimum size of password to check."))
        max_spaces = int(input("Enter the maximum size of password to check."))
        print()
        if min_spaces < max_spaces:
            max_spaces += 1
            break
        print("Maximum password size must be larger than minimum size. Please enter again.")
    except ValueError:
        print("You must enter a number into the prompt.")

manager = ThreadManager(threads)
master = MasterThread(manager)
master.start()
thread_info = ThreadInfo(threads)

prev_current_time = string_to_float(now())
for i in range(min_spaces, max_spaces):
    for combination in itertools.product(symbols, repeat=i):
        gen_pwd = (''.join(map(str, combination)))
        if not len(gen_pwd) > max_spaces:
            thread_toCheck = thread_pwd.ThreadPwd(gen_pwd, pdf)
            while not master.manager.add_thread(thread_toCheck): #if no thread was created, try again until it is
                pass

        if not master.isAlive():
            if master.manager.exc_info:
                if str(master.manager.exc_info[0]) == '<class \'thread_pwd.FoundPwd\'>':
                    found = True
                    found_pwd = str(manager.exc_info[1])
                    break
        if tested % 100 == 0 and not tested == 0:
            print("Testing Passwords....")
        check = 1000
        if tested % check == 0:
            current_time = string_to_float(now())
            cycle_time = current_time - prev_current_time
            print("\nTested " + str(tested) + " password combinations.")
            prev_current_time = current_time
            print(gen_pwd + " is the last added to threads")
            if not tested == 0:
                print("Current cycle time: " + float_to_str(cycle_time))
                avg_time = math.ceil((cycle_time / check) * 1000)/1000.0
                pass_per_min = math.ceil((60/avg_time))
                if pass_per_min > best_avg_ppm:
                    best_avg_ppm = pass_per_min
                    best_avg_threads = master.manager.max_threads

                #checking to see if threads should be increased, decreased, or remain the same
                increased_last = thread_info.change_threads(pass_per_min, increased_last)
                master.change_max_threads(thread_info.threads,)

                print("Avg Password check: " + float_to_str(avg_time))
                print(str(pass_per_min) + " passwords per minute.")
                prev_pass_per_min = pass_per_min
                print()
                print("Current best passwords-per-minute: " + str(best_avg_ppm))
                print("Threads used for best: " + str(best_avg_threads))
            print()
        tested += 1
        if found:
            break
######################################
#End of while True loop

if found:
    print("Found pass of: " + found_pwd)
    pwd_found_file = open('found_pwd.txt', 'w')
    pwd_found_file.write(found_pwd)
    pwd_found_file.close()
else:
    print("No password found with given info.")
input("Press Enter to Exit.")