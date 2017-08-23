#!/usr/bin/env python
#######################################################################
#  ngfec_auto.py						      #
#								      #
#  Sends a list of commands to ngFEC specified in the input file and  #
#  returns a list of dictionaries with the following key:value pairs  #
#								      #
#  cmd : [command inputted]					      #
#  result : [result of executed command]			      #
#  times: [elapsed time to execute command]			      #
#								      #
#######################################################################

import sys
#import makePlots as mp
from sendCommands import *
from argparse import ArgumentParser
import re
import time

# Regex to search for floats 
# (?<!_)    NOT preceeded by _
# \d+       at least one decimal number (0-9)
# \.        includes a .
r = re.compile(r"(?<!_)\d+\.\d+")

parser = ArgumentParser()
parser.add_argument("cmds", help="text file containing list of ngFEC commands")
parser.add_argument("time", help="total time for measurement")
args = parser.parse_args()

cmdList = []
with open(args.cmds, 'r') as f:
    for line in f:
        l = line.strip()
        if l != "":	# Only consider non-empty lines
            cmdList.append(line.strip())

results = send_commands(cmds=cmdList,script=True,port=64400,control_hub='hcal904daq04')

date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print "-------------------------------------"
print "| ngFEC output:\t%s |" % date 
print "-------------------------------------"
runtime = 0
step = 5 # seconds 
totaltime = int(args.time)
print "total time: {0}".format(totaltime)
while runtime < totaltime:
    for i, line in enumerate(results):
        print line['cmd']
        print "time: {0}".format(runtime)
        # Extracts all the float values from a command output into a list
        vals = r.findall(line['result'])
        for val in vals:
            print val
        '''
        if i == 0:
            mp.plot(date, vals, "Relative Humidity", "images/")
        elif i == 1:
            mp.plot(date, vals, "Temperature in deg C", "images/")
        '''
    time.sleep(step)
    runtime += step



