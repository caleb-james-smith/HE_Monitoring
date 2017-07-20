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
from ROOT import TGraph, TH1D, TCanvas, TPad, gStyle, kRed, kBlue, kGreen, kCyan, kOrange
ROOT.gROOT.SetBatch(True)   # Don't display the canvas when drawing

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
# \d+       at least one decimal number (0-9)
# \.        includes a .
r = re.compile(r"\d+\.\d+")



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

    results = send_commands(cmds=cmdList,script=True,port=64000,control_hub='hcal904daq04')
    temps = []
    hums = []
    volts = []
    peltV = []
    leakI = []

    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#    print "-------------------------------------"
#    print "| ngFEC output:\t%s |" % time 
#    print "-------------------------------------"
    for line in results:
	# Extracts all the float values from a command output into a list
	if line['cmd'].find("temperature") >= 0:
	    if line['result'].find("ERROR") >= 0:
		temps = [-1 for y in range(4)]
	    else:
		temps = [float(x) for x in r.findall(line['result'])]
	    #print "Number of temps:", len(temps)
	elif line['cmd'].find("humidity") >= 0:
	    if line['result'].find("ERROR") >= 0:
		hums = [-1 for y in range(4)]
	    else:
		hums = [float(x) for x in r.findall(line['result'])]
	    #print "Number of hums:", len(hums)
	elif line['cmd'].find("Voltage") >= 0: 
	    if line['result'].find("ERROR") >= 0:
		volts = [-1 for y in range(4)]
	    else:
		volts = [float(x) for x in r.findall(line['result'])]
	    #print "Number of volts:", len(volts)
	elif line['cmd'].find("PeltierCurrent") >= 0:
	    if line['result'].find("ERROR") >= 0:
		peltV = [-1 for y in range(4)]
	    else:
		peltV = [float(x) for x in r.findall(line['result'])]
	    #print "Number of pelt currents:", len(peltV)
	
	elif line['cmd'].find("LeakageCurrent") >= 0:
	    if line['result'].find("ERROR") >= 0:
		I = [-1 for y in range(12)]
	    else:
		I = [float(x) for x in r.findall(line['result'])]
	    leakI.extend(I)
	    print line['cmd'],  "\tNum leak currents: ", len(I)
	

    print "Temps"
    print temps

    print "Humidities"
    print hums

    print "Peltier Voltages"
    print volts

    print "Peltier Currents"
    print peltV

    print "Leakage Currents: ", len(leakI)
    print leakI

    with open(args.log, "a+") as f:
	f.write("%s" % time)
	for x in temps:
	    f.write("\t%f" % x)
	for x in hums:
	    f.write("\t%f" % x)
	for x in volts:
	    f.write("\t%f" % x)
	for x in peltV:
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
    peltVH = TH1D("peltV", "RBX Peltier Voltage (V)", len(volts), 0.5, len(volts)+0.5)
    peltVH.SetFillColor(kCyan)
    for i,t in enumerate(volts):
	peltVH.Fill(i+1, t)

    peltVH.GetXaxis().SetTitle("RM")
    peltVH.GetYaxis().SetTitle("Voltage (V)")
    peltVH.GetYaxis().SetTitleOffset(2.1)
    peltVH.GetXaxis().SetNdivisions(len(volts))

    plotHisto(peltVH, "plots/peltV.png")


    # Peltier current
    peltIH = TH1D("peltI", "RBX Peltier Current (A)", len(peltV), 0.5, len(peltV)+0.5)
    peltIH.SetFillColor(kGreen)
    for i,t in enumerate(peltV):
	peltIH.Fill(i+1, t)

    peltIH.GetXaxis().SetTitle("RM")
    peltIH.GetYaxis().SetTitle("Current (A)")
    peltIH.GetYaxis().SetTitleOffset(2.1)
    peltIH.GetXaxis().SetNdivisions(len(peltV))

    plotHisto(peltIH, "plots/peltI.png")


    # Leakage current
    leakIH = TH1D("leakI", "RBX Leakage Current (mA)", len(leakI), 0.5, len(leakI)+0.5)
    leakIH.SetFillColor(kOrange)
    for i,t in enumerate(leakI):
	leakIH.Fill(i+1, t)

    leakIH.GetXaxis().SetTitle("SiPM")
    leakIH.GetYaxis().SetTitle("Current (mA)")
    leakIH.GetXaxis().SetTickLength(0)
    leakIH.GetXaxis().SetLabelOffset(999.0)
    leakIH.GetYaxis().SetTitleOffset(2.1)
    leakIH.GetXaxis().SetNdivisions(len(leakI))

    plotHisto(leakIH, "plots/leakI.png")


if __name__ == "__main__":
    sys.exit(main())
