#!/usr/bin/env python
#######################################################################
#  ngfec_auto.py                                                      #
#                                                                     #
#  Sends a list of commands to ngFEC specified in the input file and  #
#  returns a list of dictionaries with the following key:value pairs  #
#                                                                     #
#  cmd : [command inputted]                                           #
#  result : [result of executed command]                              #
#  times: [elapsed time to execute command]                           #
#                                                                     #
#######################################################################

import sys
#import makePlots as mp
from sendCommands import *
from argparse import ArgumentParser
from statPlot import plotHisto
import re
import time
import ROOT
from ROOT import TGraph, TH1D, TCanvas, TPad, gStyle, kRed, kBlue, kGreen, kCyan, kOrange, kViolet, kMagenta
ROOT.gROOT.SetBatch(True)   # Don't display the canvas when drawing

#port = 64000
#port = 64400
#control_hub = "cmshcaltb03"
control_hub = "hcal904daq04"

# Stat options
# e: entries 
# m: mean
# r: std dev
#gStyle.SetOptStat("emr")
#gStyle.SetStatW(0.16)
#gStyle.SetStatH(0.133)
#gStyle.SetStatX(1.0)
#gStyle.SetStatY(1.0)
gStyle.SetOptStat(0)

# Regex to search for floats 
# (?<=\s)   positive lookbehind (preceeded by) \s, whitespace character
# \d+       at least one decimal number (0-9)
# \.        includes a .
#r = re.compile(r"\d+\.\d+")
r = re.compile(r"(?<=\s)\d+\.\d+")

# Search for results that either end in a decimal number, whitespace, or $ (eg 115.$)
r_retry = re.compile(r"((?<=\s)\d+\.(\d+|(?=\s)|(?=\$)))")

# Regex to search for total number of entries expected from an ngccm command
# (?<=-)    positive lookbehind for -
# \d+       at least one decimal number (0-9)
# (?=])     positive lookahead (tailed by) ]
r_entry = re.compile(r"(?<=-)\d+(?=])")

def retrySendCmd(cmd, expectedNum, port):
    # Using script=False works with one command and will return the raw output
    raw = send_commands(cmds=cmd,script=False,port=port,control_hub=control_hub)
    I = []
    if raw[0]['result'].find("ERROR") >= 0:
        I = [-1 for y in range(expectedNum)]
    else:
        #print "Raw result:"
        #print raw[0]['result']
        #print "regex result "
        #print r_retry.findall(raw[0]['result'])
        I = [float(x[0]) for x in r_retry.findall(raw[0]['result'])]
    return I 

# get command list from file
def getCmdList(cmdFile):
    cmdList = []
    with open(cmdFile, 'r') as f:
        for line in f:
            l = line.strip()
            if l != "": # Only consider non-empty lines
                cmdList.append(line.strip())
    return cmdList

# get command string from command list
def getCmdString(cmdList):
    cmdString = ""
    sets = ["[1-4]", "[1-64]"]
    set_values = [4, 64]
    joiner = "{:<40}"
    for cmd in cmdList:
        cmd = cmd.strip("get ")
        cmd = cmd.strip("tget ")
        counts = list(cmd.count(a) for a in sets)
        # does not contain either set
        if counts[0] == 0 and counts[1] == 0:
            #print "no sets: {0}".format(cmd)
            cmdString += joiner.format(cmd)
        # contains both sets once
        elif counts[0] == 1 and counts[1] == 1:
            iset_1 = 0
            iset_2 = 1
        # contains the first set twice but not the second set
        elif counts[0] == 2 and counts[1] == 0:
            iset_1 = 0
            iset_2 = 0
        if (counts[0] == 1 and counts[1] == 1) or (counts[0] == 2 and counts[1] == 0):
            first_split = cmd.split(sets[iset_1])
            if len(first_split) > 2:
                split_cmd = first_split
            else:
                second_split = first_split[1].split(sets[iset_2])
                split_cmd = [first_split[0]] + second_split
            for j in xrange(1,set_values[iset_1]+1):
                for k in xrange(1,set_values[iset_2]+1):
                    joined = split_cmd[0] + str(j) + split_cmd[1] + str(k) + split_cmd[2]
                    #print "j={0} k={1} {2}".format(j,k,joined)
                    cmdString += joiner.format(joined)
        # contains the first set once but not the second set
        elif counts[0] == 1 and counts[1] == 0:
            iset = 0
        # contains the second set once but not the first set
        elif counts[0] == 0 and counts[1] == 1:
            iset = 1
        if  (counts[0] == 1 and counts[1] == 0) or (counts[0] == 0 and counts[1] == 1):
            split_cmd = cmd.split(sets[iset])
            for j in xrange(1,set_values[iset]+1):
                joined = str(j).join(split_cmd)
                #print "j={0} {1}".format(j,joined)
                cmdString += joiner.format(joined)
    
    return cmdString

def main():
    parser = ArgumentParser()
    parser.add_argument("cmds", help="text file containing list of ngFEC commands")
    parser.add_argument("--log",  "-o", default="rbxMonitor.log", help="log file to save stats in")
    parser.add_argument("--port", "-p", default=64000, help="port for ngccm server")
    args = parser.parse_args()
    port = args.port

    cmdList = getCmdList(args.cmds)
    #simpleCmdString = " ".join(cmdList)
    #fullCmdString = getCmdString(cmdList)
    #print simpleCmdString
    #print fullCmdString

    results = send_commands(cmds=cmdList,script=True,port=port,control_hub=control_hub)
    params = {}
    params["temps"] = []
    params["hums"] = []
    params["peltV"] = []
    params["peltI"] = []
    params["BVin"] = []
    params["Vin"] = []
    params["leakI"] = []
    params["cardT"] = []
    params["setV"] = []
    params["targetT"] = []
    names = {}
    names["temps"] = "rtdtemperature"
    names["hums"] = "humidity"
    names["peltV"] = "PeltierVoltage"
    names["peltI"] = "PeltierCurrent"
    names["BVin"] = "-BVin"
    names["Vin"] = "-Vin"
    names["leakI"] = "LeakageCurrent"
    names["cardT"] = "SHT_temp"
    names["setV"] = "SetPeltierVoltage"
    names["targetT"] = "targettemperature"
    expectedEntries = {}    # Expected number of entries for each command

    # Determine how many entries to expect from each command to know if it needs to be run again
    # Pexpect likes to truncate results..
    for c in cmdList:
        entries = 1
        parsedCmd = r_entry.findall(c)
        for x in parsedCmd:
            entries *= int(x)
        expectedEntries[c] = entries

    #for a in expectedEntries.keys():
    #    print a, "\t", expectedEntries[a]

    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#    print "-------------------------------------"
#    print "| ngFEC output:\t%s |" % time 
#    print "-------------------------------------"
    for line in results:
        # Extracts all the float values from a command output into a list

        for key in params:
            if line['cmd'].find(names[key]) >= 0:
                exp = expectedEntries[line['cmd']]
                if line['result'].find("ERROR") >= 0:
                    params[key] = [-1 for y in range(exp)]
                else:
                    values = [float(x) for x in r.findall(line['result'])]
                    params[key] = values
                    name = names[key]
                    if len(values) != exp:
                        print "{0}: {1} expected number: {2}".format(name, len(values), exp)
                        values = retrySendCmd(line['cmd'], exp, port)
                        params[key] = values
                        print "After retrying {0}:".format(name)
                        print "{0}: {1} expected number: {2}".format(name, len(values), exp)

        '''
        if line['cmd'].find("temperature") >= 0:
            exp = expectedEntries[line['cmd']]
            if line['result'].find("ERROR") >= 0:
                params["temps"] = [-1 for y in range(exp)]
            else:
                params["temps"] = [float(x) for x in r.findall(line['result'])]
                if len(temps) != exp:
                    #print line['result']
                    temps = params["temps"]
                    print "Temps:", len(temps), "\tExpected number:", exp
                    temps = retrySendCmd(line['cmd'], exp, port)
                    print "After retrying temps:"
                    print "Temps:", len(temps), "\tExpected number:", exp
        
        elif line['cmd'].find("humidity") >= 0:
            exp = expectedEntries[line['cmd']]
            if line['result'].find("ERROR") >= 0:
                hums = [-1 for y in range(exp)]
            else:
                hums = [float(x) for x in r.findall(line['result'])]
                if len(hums) != exp:
                    #print line['result']
                    print "Hums:", len(hums), "\tExpected number:", exp
                    hums = retrySendCmd(line['cmd'], exp, port)
                    print "After retrying hums:"
                    print "Hums:", len(hums), "\tExpected number:", exp
        
        elif line['cmd'].find("PeltierVoltage") >= 0: 
            exp = expectedEntries[line['cmd']]
            if line['result'].find("ERROR") >= 0:
                peltV = [-1 for y in range(exp)]
            else:
                peltV = [float(x) for x in r.findall(line['result'])]
                if len(peltV) != exp:
                    #print line['result']
                    print "peltV:", len(peltV), "\tExpected number:", exp
                    peltV = retrySendCmd(line['cmd'], exp, port)
                    print "After retrying peltV:"
                    print "peltV:", len(peltV), "\tExpected number:", exp
        
        elif line['cmd'].find("PeltierCurrent") >= 0:
            exp = expectedEntries[line['cmd']]
            if line['result'].find("ERROR") >= 0:
                peltI = [-1 for y in range(exp)]
            else:
                peltI = [float(x) for x in r.findall(line['result'])]
                if len(peltI) != exp:
                    #print line['cmd']
                    #print line['result']
                    print "peltI:", len(peltI), "\tExpected number:", exp
                    peltI = retrySendCmd(line['cmd'], exp, port)
                    print "After retrying peltI:"
                    print "peltI:", len(peltI), "\tExpected number:", exp

        elif line['cmd'].find("-BVin") >= 0:
            exp = expectedEntries[line['cmd']]
            if line['result'].find("ERROR") >= 0:
                BVin = [-1 for y in range(exp)]
            else:
                BVin = [float(x) for x in r.findall(line['result'])]
                if len(BVin) != exp:
                    #print line['result']
                    print "BVin:", len(BVin), "\tExpected number:", exp
                    BVin = retrySendCmd(line['cmd'], exp, port)
                    print "After retrying BVin:"
                    print "BVin:", len(BVin), "\tExpected number:", exp
  
        elif line['cmd'].find("-Vin") >= 0:
            exp = expectedEntries[line['cmd']]
            if line['result'].find("ERROR") >= 0:
                Vin = [-1 for y in range(exp)]
            else:
                Vin = [float(x) for x in r.findall(line['result'])]
                if len(Vin) != exp:
                    #print line['result']
                    print "Vin:", len(Vin), "\tExpected number:", exp
                    Vin = retrySendCmd(line['cmd'], exp, port)
                    print "After retrying Vin:"
                    print "Vin:", len(Vin), "\tExpected number:", exp
    
        elif line['cmd'].find("LeakageCurrent") >= 0:
            exp = expectedEntries[line['cmd']]
            if line['result'].find("ERROR") >= 0:
                leakI = [-1 for y in range(exp)]
            else:
                leakI = [float(x) for x in r.findall(line['result'])]
                if len(leakI) != exp:
                    print "leakI:", len(leakI), "\tExpected number:", exp
                    leakI = retrySendCmd(line['cmd'], exp, port)
                    print "After retrying leakI:"
                    print "leakI:", len(leakI), "\tExpected number:", exp
    
        '''

    with open(args.log, "a+") as f:
        f.write("%s " % time)
        x = ""
        for key in params:
            for value in params[key]:
                x += "{0} ".format(value)
        print "x: {0}".format(x)
        f.write(x + "\n")
        
    ''' 
    # Temperature 
    tempH = TH1D("Temp", "RBX Temperature (^{o}C)", len(temps), 0.5, len(temps)+0.5)
    tempH.SetFillColor(kRed)
    for i,t in enumerate(temps):
        tempH.Fill(i+1, t)
        
    tempH.GetXaxis().SetTitle("RM")
    tempH.GetYaxis().SetTitle("Temp (^{o}C)")
    tempH.GetYaxis().SetTitleOffset(2.1)
    tempH.GetXaxis().SetNdivisions(len(temps))

    plotHisto(tempH, "plots/temp.png")


    # Humidity
    humH = TH1D("Humidity", "RBX Humidity (%)", len(hums), 0.5, len(hums)+0.5)
    humH.SetFillColor(kBlue)
    for i,h in enumerate(hums):
        humH.Fill(i+1, h)

    humH.GetXaxis().SetTitle("RM")
    humH.GetYaxis().SetTitle("Humidity (%)")
    humH.GetYaxis().SetTitleOffset(2.1)
    humH.GetXaxis().SetNdivisions(len(hums))

    plotHisto(humH, "plots/hum.png")


    # Peltier voltage 
    peltVH = TH1D("peltV", "RBX Peltier Voltage (V)", len(peltV), 0.5, len(peltV)+0.5)
    peltVH.SetFillColor(kCyan+1)
    for i,t in enumerate(peltV):
        peltVH.Fill(i+1, t)

    peltVH.GetXaxis().SetTitle("RM")
    peltVH.GetYaxis().SetTitle("Voltage (V)")
    peltVH.GetYaxis().SetTitleOffset(2.1)
    peltVH.GetXaxis().SetNdivisions(len(peltV))

    plotHisto(peltVH, "plots/peltV.png")


    # Peltier current
    peltIH = TH1D("peltI", "RBX Peltier Current (A)", len(peltI), 0.5, len(peltI)+0.5)
    peltIH.SetFillColor(kGreen+2)
    for i,t in enumerate(peltI):
        peltIH.Fill(i+1, t)

    peltIH.GetXaxis().SetTitle("RM")
    peltIH.GetYaxis().SetTitle("Current (A)")
    peltIH.GetYaxis().SetTitleOffset(2.1)
    peltIH.GetXaxis().SetNdivisions(len(peltI))

    plotHisto(peltIH, "plots/peltI.png")

    
    # BVin 
    BVinH = TH1D("BVin", "RBX Bulk Bias Voltage In (V)", len(BVin), 0.5, len(BVin)+0.5)
    BVinH.SetFillColor(kViolet+1)
    for i,t in enumerate(BVin):
        BVinH.Fill(i+1, t)

    BVinH.GetXaxis().SetTitle("RM")
    BVinH.GetYaxis().SetTitle("Voltage (V)")
    BVinH.GetYaxis().SetTitleOffset(2.1)
    BVinH.GetXaxis().SetNdivisions(len(BVin))

    plotHisto(BVinH, "plots/BVin.png")

    
    # Vin 
    VinH = TH1D("Vin", "RBX Backplane Voltage In (V)", len(Vin), 0.5, len(Vin)+0.5)
    VinH.SetFillColor(kMagenta)
    for i,t in enumerate(Vin):
        VinH.Fill(i+1, t)

    VinH.GetXaxis().SetTitle("RM")
    VinH.GetYaxis().SetTitle("Voltage (V)")
    VinH.GetYaxis().SetTitleOffset(2.1)
    VinH.GetXaxis().SetNdivisions(len(Vin))

    plotHisto(VinH, "plots/Vin.png")

    # Leakage current
    leakIH = TH1D("leakI", "SiPM Leakage Current (\muA)", len(leakI), 0.5, len(leakI)+0.5)
    leakIH.SetFillColor(kOrange)
    for i,t in enumerate(leakI):
        leakIH.Fill(i+1, t)

    leakIH.GetXaxis().SetTitle("SiPM [1-192]")
    leakIH.GetYaxis().SetTitle("Current (\muA)")
    leakIH.GetXaxis().SetTickLength(0)
    leakIH.GetXaxis().SetLabelOffset(999.0)
    leakIH.GetYaxis().SetTitleOffset(2.1)
    leakIH.GetXaxis().SetNdivisions(len(leakI))

    plotHisto(leakIH, "plots/leakI.png")
    '''


if __name__ == "__main__":
    sys.exit(main())
