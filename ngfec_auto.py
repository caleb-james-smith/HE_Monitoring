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
import ROOT
from ROOT import TGraph, TH1D, TCanvas, TPad, gStyle, kRed, kBlue, kGreen, kCyan, kOrange
ROOT.gROOT.SetBatch(True)
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
temps = []
hums = []
volts = []
peltCur = []
leakCur = []

time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print "-------------------------------------"
print "| ngFEC output:\t%s |" % time 
print "-------------------------------------"
for line in results:
    # Extracts all the float values from a command output into a list
    #print line['cmd']
    #print line['result']
    if line['cmd'].find("temperature") >= 0:
	temps = [float(x) for x in r.findall(line['result'])]
	#print temps
	print "Number of temps:", len(temps)
    elif line['cmd'].find("humidity") >= 0:
	hums = [float(x) for x in r.findall(line['result'])]
	#print hums
	print "Number of hums:", len(hums)
    elif line['cmd'].find("Voltage") >= 0:
	volts = [float(x) for x in r.findall(line['result'])]
	print "Number of volts:", len(volts)
    elif line['cmd'].find("PeltierCurrent") >= 0:
	peltCur = [float(x) for x in r.findall(line['result'])]
	print "Number of pelt currents:", len(peltCur)
    
    elif line['cmd'].find("LeakageCurrent") >= 0:
	x = [float(x) for x in r.findall(line['result'])]
	leakCur.extend(x)
	print line['cmd'],  "\tNum leak currents: ", len(x)
    

print "Temps"
print temps

print "Humidities"
print hums

print "Peltier Voltages"
print volts

print "Peltier Currents"
print peltCur

print "Leakage Currents: ", len(leakCur)
print leakCur

with open("statLog.txt", "a+") as f:
    #f.write("%s\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f\n" % (time, temps[0], temps[1], temps[2], temps[3], hums[0], hums[1], hums[2], hums[3]))
    f.write("%s" % time)
    for x in temps:
	f.write("\t%f" % x)
    for x in hums:
	f.write("\t%f" % x)
    for x in volts:
	f.write("\t%f" % x)
    for x in peltCur:
	f.write("\t%f" % x)
    for x in leakCur:
	f.write("\t%f" % x)
    f.write("\n")

# Stat options
# n: name
# e: entries 
# m: mean
# r: std dev
gStyle.SetOptStat("emr")

# Temperature plots
tempG = TGraph()
tempG.SetLineWidth(2)
tempG.SetLineColor(kRed)
tempH = TH1D("Temp", "RBX Temperatures (^{o}C)", len(temps), 0.5, len(temps)+0.5)
tempH.SetFillColor(kRed)
for i,t in enumerate(temps):
    tempG.SetPoint(i, i+1, t)
    tempH.Fill(i+1, t)

c = TCanvas("c", "c", 1200, 1200)
pad = TPad("p","p", 0.05,0.0, 1.0, 1.0)
pad.cd()
tempG.SetTitle("RBX Temperatures (^{o}C)")
tempG.GetXaxis().SetTitle("RM")
tempG.GetYaxis().SetTitle("Temp (^{o}C)")
tempG.GetYaxis().SetTitleOffset(2.1)
tempG.GetXaxis().SetNdivisions(len(temps))
tempG.Draw()
c.cd()
pad.Draw()
#c.SaveAs("tempG.jpg")


c.Clear()
pad = TPad("p","p", 0.05,0.0, 1.0, 1.0)
pad.cd()
tempH.SetTitle("RBX Temperatures (^{o}C)")
tempH.GetXaxis().SetTitle("RM")
tempH.GetYaxis().SetTitle("Temp (^{o}C)")
tempH.GetYaxis().SetTitleOffset(2.1)
tempH.GetXaxis().SetNdivisions(len(temps))
tempH.Draw("HIST")
c.cd()
pad.Draw()
c.SaveAs("tempH.jpg")


# Humidity plots
c.Clear()
humG = TGraph()
humG.SetLineWidth(2)
humG.SetLineColor(kBlue)
humG.SetTitle("RBX Humidities (%);RM;Humidity (%)")
humH = TH1D("Humidity", "RBXHumidity (%)", len(hums), 0.5, len(hums)+0.5)
humH.SetFillColor(kBlue)
for i,h in enumerate(hums):
    humG.SetPoint(i, i+1, h)
    humH.Fill(i+1, h)

pad = TPad("p","p", 0.05,0.0, 1.0, 1.0)
pad.cd()
humG.SetTitle("RBX Humidities (%)")
humG.GetXaxis().SetTitle("RM")
humG.GetYaxis().SetTitle("Humidity (%)")
humG.GetYaxis().SetTitleOffset(2.1)
humG.GetXaxis().SetNdivisions(len(hums))
humG.Draw()
c.cd()
pad.Draw()
humG.Draw()
#c.SaveAs("humG.jpg")


c.Clear()
pad = TPad("p","p", 0.05,0.0, 1.0, 1.0)
pad.cd()
humH.GetXaxis().SetTitle("RM")
humH.GetYaxis().SetTitle("Humidity (%)")
humH.GetXaxis().SetNdivisions(len(hums))
humH.Draw("HIST")
c.cd()
pad.Draw()
c.SaveAs("humH.jpg")


# Peltier voltage plots
c.Clear()
voltG = TGraph()
voltG.SetLineWidth(2)
voltG.SetLineColor(kCyan)
voltH = TH1D("Volt", "RBX Peltier Voltages (V)", len(volts), 0.5, len(volts)+0.5)
voltH.SetFillColor(kCyan)
for i,t in enumerate(volts):
    voltG.SetPoint(i, i+1, t)
    voltH.Fill(i+1, t)

pad = TPad("p","p", 0.05,0.0, 1.0, 1.0)
pad.cd()
voltG.SetTitle("RBX Peltier Voltages (V)")
voltG.GetXaxis().SetTitle("RM")
voltG.GetYaxis().SetTitle("Voltage (V)")
voltG.GetYaxis().SetTitleOffset(2.1)
voltG.GetXaxis().SetNdivisions(len(volts))
voltG.Draw()
c.cd()
pad.Draw()
#c.SaveAs("voltG.jpg")


c.Clear()
pad = TPad("p","p", 0.05,0.0, 1.0, 1.0)
pad.cd()
voltH.SetTitle("RBX Peltier Voltages (V)")
voltH.GetXaxis().SetTitle("RM")
voltH.GetYaxis().SetTitle("Voltage (V)")
voltH.GetYaxis().SetTitleOffset(2.1)
voltH.GetXaxis().SetNdivisions(len(volts))
voltH.Draw("HIST")
c.cd()
pad.Draw()
c.SaveAs("voltH.jpg")


# Peltier current plots
c.Clear()
pCurG = TGraph()
pCurG.SetLineWidth(2)
pCurG.SetLineColor(kGreen)
pCurH = TH1D("peltCur", "RBX Peltier Currents (A)", len(peltCur), 0.5, len(peltCur)+0.5)
pCurH.SetFillColor(kGreen)
for i,t in enumerate(peltCur):
    pCurG.SetPoint(i, i+1, t)
    pCurH.Fill(i+1, t)

pad = TPad("p","p", 0.05,0.0, 1.0, 1.0)
pad.cd()
pCurG.SetTitle("RBX Peltier Currents (A)")
pCurG.GetXaxis().SetTitle("RM")
pCurG.GetYaxis().SetTitle("Current (A)")
pCurG.GetYaxis().SetTitleOffset(2.1)
pCurG.GetXaxis().SetNdivisions(len(peltCur))
pCurG.Draw()
c.cd()
pad.Draw()
#c.SaveAs("pCurG.jpg")


c.Clear()
pad = TPad("p","p", 0.05,0.0, 1.0, 1.0)
pad.cd()
pCurH.SetTitle("RBX Peltier Currents (A)")
pCurH.GetXaxis().SetTitle("RM")
pCurH.GetYaxis().SetTitle("Current (A)")
pCurH.GetYaxis().SetTitleOffset(2.1)
pCurH.GetXaxis().SetNdivisions(len(peltCur))
pCurH.Draw("HIST")
c.cd()
pad.Draw()
c.SaveAs("pCurH.jpg")


# Leakage current plots
c.Clear()
lCurH = TH1D("leakCur", "RBX Leakage Currents (A)", len(leakCur), 0.5, len(leakCur)+0.5)
lCurH.SetFillColor(kOrange)
for i,t in enumerate(leakCur):
    lCurH.Fill(i+1, t)

pad = TPad("p","p", 0.05,0.0, 1.0, 1.0)
pad.cd()
lCurH.SetTitle("RBX Leakage Currents (mA)")
lCurH.GetXaxis().SetTitle("QIE RM[1-4]-[1-48]")
lCurH.GetYaxis().SetTitle("Current (mA)")
lCurH.GetYaxis().SetTitleOffset(2.1)
lCurH.GetXaxis().SetNdivisions(len(leakCur))
lCurH.Draw("HIST")
c.cd()
pad.Draw()
c.SaveAs("lCurH.jpg")
