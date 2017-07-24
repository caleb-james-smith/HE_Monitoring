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
from statPlot import plotHisto
import re
import ROOT
from ROOT import TGraph, TH1D, TCanvas, TPad, gStyle, kRed, kBlue, kGreen, kCyan, kOrange, kViolet, kMagenta
ROOT.gROOT.SetBatch(True)   # Don't display the canvas when drawing

port = 64000
control_hub = "cmshcaltb03"

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

def retrySendCmd(cmd, expectedNum):
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


def main():
    parser = ArgumentParser()
    parser.add_argument("cmds", help="text file containing list of ngFEC commands")
    parser.add_argument("--log", "-o", default="rbxMonitor.log", help="log file to save stats in")
    args = parser.parse_args()

    cmdList = []
    with open(args.cmds, 'r') as f:
	for line in f:
	    l = line.strip()
	    if l != "":	# Only consider non-empty lines
		cmdList.append(line.strip())

    results = send_commands(cmds=cmdList,script=True,port=port,control_hub=control_hub)
    temps = []
    hums = []
    peltV = []
    peltI = []
    BVin = []
    Vin = []
    leakI = []
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
	if line['cmd'].find("temperature") >= 0:
            exp = expectedEntries[line['cmd']]
	    if line['result'].find("ERROR") >= 0:
		temps = [-1 for y in range(exp)]
	    else:
		temps = [float(x) for x in r.findall(line['result'])]
                if len(temps) != exp:
                    #print line['result']
                    print "Temps:", len(temps), "\tExpected number:", exp
                    temps = retrySendCmd(line['cmd'], exp)
                    print "After retrying temps:"
                    print temps
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
                    hums = retrySendCmd(line['cmd'], exp)
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
                    peltV = retrySendCmd(line['cmd'], exp)
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
                    peltI = retrySendCmd(line['cmd'], exp)
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
                    BVin = retrySendCmd(line['cmd'], exp)
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
                    Vin = retrySendCmd(line['cmd'], exp)
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
                    leakI = retrySendCmd(line['cmd'], exp)
                    print "After retrying leakI:"
                    print "leakI:", len(leakI), "\tExpected number:", exp
    
    print "Temps:", len(temps)
    print temps

    print "Humidities:", len(hums)
    print hums

    print "Peltier Voltages:", len(peltV)
    print peltV

    print "Peltier Currents:", len(peltI)
    print peltI

    print "BVin:", len(BVin)
    print BVin

    print "Vin:", len(Vin)
    print Vin
    
    print "LeakI:", len(leakI)
    print leakI
    
    with open(args.log, "a+") as f:
	f.write("%s" % time)
	for x in temps:
	    f.write("\t%f" % x)
	for x in hums:
	    f.write("\t%f" % x)
	for x in peltV:
	    f.write("\t%f" % x)
	for x in peltI:
	    f.write("\t%f" % x)
        for x in BVin:
            f.write("\t%f" % x)
        for x in Vin:
            f.write("\t%f" % x)
        for x in leakI:
	    f.write("\t%f" % x)
	f.write("\n")

    
    
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


if __name__ == "__main__":
    sys.exit(main())
