"""
This module was created by Paul McGuire:
http://stackoverflow.com/users/165216/paul-mcguire
http://pyparsing.wikispaces.com
"""


import atexit
from time import clock
from functools import reduce
import math

def secondsToStr(t):
  return "%d:%02d:%02d:%03d" % \
        reduce(lambda ll,b : divmod(ll[0],b) + ll[1:],
            [(t*1000,),1000,60,60])

line = "="*40
def log(s, elapsed=None):
    print (line)
    print (secondsToStr(clock()), '-', s)
    if elapsed:
        print ("Elapsed time:", elapsed)
    print (line)

def endlog():
    end = clock()
    elapsed = end-start
    log("End Program", secondsToStr(elapsed))

def now():
    return secondsToStr(clock())


##############################
####These were added by me####
##############################
def string_to_float(t):
    parts = t.split(':')
    total = int(parts[0]) * 60#hours
    total = total + int(parts[1])#minutes
    total = total * 60
    total - total * 100
    total = total + int(parts[2])#seconds
    total = total + (float(parts[3]) / 1000.0)
    return total

def float_to_str(t):
    try:
        decimal_mod = math.ceil(math.modf(t)[0] * 1000)
    except TypeError:
        decimal_mod = 0.0
    decimal = str(decimal_mod)
    if decimal_mod * 1000 < 10:
        decimal = "00" + decimal
    if decimal_mod * 1000 < 100:
        decimal = "0" + decimal

    remainder = t - (decimal_mod/1000.0)
    remainder = int(remainder)
    seconds = remainder % 100
    remainder = (remainder - seconds) / 100
    minutes = int(remainder % 60)
    remainder = remainder - minutes
    hours = remainder / 60
    to_return = str(hours) + ":" + str(minutes) + ":" + str(seconds) + ":" + str(decimal)

    return to_return


start = clock()
atexit.register(endlog)
#log("Start Program")