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
from sendCommands import *
from argparse import ArgumentParser
import re

# Regex to search for floats 
# (?<!_)    NOT preceeded by _
# \d+       at least one decimal number (0-9)
# \.        includes a .
r = re.compile(r"(?<!_)\d+\.\d+")

parser = ArgumentParser()
parser.add_argument("cmds", help="text file containing list of ngFEC commands")
args = parser.parse_args()

cmdList = []
with open(args.cmds, 'r') as f:
    for line in f:
	l = line.strip()
	if l != "":	# Only consider non-empty lines
    	    cmdList.append(line.strip())

results = send_commands(cmds=cmdList,script=True,port=64000,control_hub='hcal904daq04')

print "-------------------------------------"
print "| ngFEC output:\t%s |" % datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print "-------------------------------------"
for line in results:
    # Extracts all the float values from a command output into a list
    vals = r.findall(line['result'])
    for val in vals:
	print val   



