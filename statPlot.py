#!/usr/bin/env python
#######################################################################
#  statPlot.py							      #
#								      #
#  Parse an ngfec_auto log file and plots stats as a function of time #
#								      #
#######################################################################

import sys
from argparse import ArgumentParser
import ROOT
from pprint import pprint
from ROOT import TGraph, TMultiGraph, TH1D, TLegend, TCanvas, TPad, gStyle, kRed, kBlue, kOrange, kCyan, kGreen, kBlack
ROOT.gROOT.SetBatch(True)

COLORS = [kRed, kCyan, kGreen, kBlack]
MARKERS = [21, 22, 29, 33] 
gStyle.SetOptStat("emr")

def plotMultiGraph(dataReadings, vals, title, xTitle, yTitle, outF):
    mg = TMultiGraph()
    cv = TCanvas(outF, "cv", 1200, 1200)
    l = TLegend(0.9, 0.7, 1.0, 0.9)
    pad = TPad("p","p", 0.05, 0.05, 1.0, 1.0)
    pad.cd()
    for rm in range(len(vals)):
	l.AddEntry(vals[rm], "RM%d" % (rm+1), "pl")
	mg.Add(vals[rm])
    mg.Draw("alp")
    pad.Update()
    mg.SetTitle(title + ";" + xTitle + ";" + yTitle)
    l.Draw()
    cv.cd()
    pad.Draw()
    
    mg.GetXaxis().SetNdivisions(len(dataReadings))
    date = "" 
    for i in range(len(dataReadings)):
	# If new date, print date and time
	if date != dataReadings[i]["date"]:
	    date = dataReadings[i]["date"]
	    mg.GetXaxis().SetBinLabel(mg.GetXaxis().FindBin(i), "#splitline{%s}{%s}"%(date, dataReadings[i]["time"]))
	else:
	    mg.GetXaxis().SetBinLabel(mg.GetXaxis().FindBin(i), dataReadings[i]["time"])

    mg.GetXaxis().SetTitleOffset(2.4)
    mg.GetYaxis().SetTitleOffset(2.1)
    pad.Update()
    cv.SaveAs(outF + "_graph.jpg")


def plotHisto(histo, outF):    
    cv = TCanvas(outF + "H", "cv", 1200, 1200)
    pad = TPad("p","p", 0.05, 0.0, 1.0, 1.0)
    pad.cd()
    histo.Draw("HIST")
    cv.cd()
    pad.Draw()
    cv.SaveAs(outF + "_histo.jpg")


def main():
    parser = ArgumentParser()
    parser.add_argument("log", help="log file from ngfec_auto")
    parser.add_argument("--min", "-n", type=int, default=None, help="lower range bound (neg vals count backwards from the end)")
    parser.add_argument("--max", "-x", type=int, default=None, help="upper range bound (neg vals count backwards from the end")
    args = parser.parse_args()

    readings = []
    minT = 9999.0
    maxT = -9999.0
    minH = 101.0
    maxH = -1.0
    # peltier voltage
    minPV = 9999.0
    maxPV = -9999.0
    # peltier current
    minPI = 9999.0
    maxPI = -9999.0
    # leakage current
    minLI = 9999.0
    maxLI = -9999.0
    
    with open(args.log, "r") as f:
	for line in f:
	    data = line.split()
	    entry = {}
	    entry["date"] = data[0]
	    entry["time"] = data[1]
	    entry["temp"] = [float(data[i]) for i in xrange(2, 6)]
	    entry["hum"]  = [float(data[i]) for i in xrange(6, 10)]
	    entry["peltV"] = [float(data[i]) for i in xrange(10, 14)]
	    entry["peltI"] = [float(data[i]) for i in xrange(14, 18)]
	    entry["leakI"] = [float(data[i]) for i in xrange(18, 210)]
	    minT = min(minT, min(entry["temp"]))
	    maxT = max(maxT, max(entry["temp"]))
	    minH = min(minH, min(entry["hum"]))
	    maxH = max(maxH, max(entry["hum"]))
	    minPV = min(minPV, min(entry["peltV"]))
	    maxPV = max(maxPV, max(entry["peltV"]))
	    minPI = min(minPI, min(entry["peltI"]))
	    maxPI = max(maxPI, max(entry["peltI"]))
	    minLI = min(minLI, min(entry["leakI"]))
	    maxLI = max(maxLI, max(entry["leakI"]))
	    readings.append(entry)
   
    readings = readings[ args.min : args.max ]

    tempG = []
    humG = []
    peltVG = []
    peltIG = []
    tempMG = TMultiGraph()
    humMG = TMultiGraph()
    peltVMG = TMultiGraph()
    peltIMG = TMultiGraph()


    for i in range(len(readings[0]["temp"])):
	tempG.append(TGraph())
	tempG[i].SetLineColor(COLORS[i])
	tempG[i].SetLineWidth(2)
	tempG[i].SetMarkerStyle(MARKERS[i])
	tempG[i].SetMarkerSize(2)
	tempG[i].SetMarkerColor(COLORS[i])

    for i in range(len(readings[0]["hum"])):
	humG.append(TGraph())
	humG[i].SetLineColor(COLORS[i])
	humG[i].SetLineWidth(2)
	humG[i].SetMarkerStyle(MARKERS[i])
	humG[i].SetMarkerSize(2)
	humG[i].SetMarkerColor(COLORS[i])

    for i in range(len(readings[0]["peltV"])):
	peltVG.append(TGraph())
	peltVG[i].SetLineColor(COLORS[i])
	peltVG[i].SetLineWidth(2)
	peltVG[i].SetMarkerStyle(MARKERS[i])
	peltVG[i].SetMarkerSize(2)
	peltVG[i].SetMarkerColor(COLORS[i])

    for i in range(len(readings[0]["peltI"])):
	peltIG.append(TGraph())
	peltIG[i].SetLineColor(COLORS[i])
	peltIG[i].SetLineWidth(2)
	peltIG[i].SetMarkerStyle(MARKERS[i])
	peltIG[i].SetMarkerSize(2)
	peltIG[i].SetMarkerColor(COLORS[i])


    tempH = TH1D("Temp", "RBX Temperatures (^{o}C)", 20, minT - 0.05, maxT + 0.05)
    tempH.SetFillColor(kRed)
    tempH.SetTitle("RBX Temperatures (^{o}C)")
    tempH.GetXaxis().SetTitle("Temp (^{o}C)")
    tempH.GetYaxis().SetTitle("Entries")
    tempH.GetYaxis().SetTitleOffset(2.1)
    
    humH = TH1D("Humidity", "RBX Humidities (%)", 20, minH - 0.5, maxH + 0.5)
    humH.SetFillColor(kBlue)
    humH.SetTitle("RBX Humidities (%)")
    humH.GetXaxis().SetTitle("Humidity (%)")
    humH.GetYaxis().SetTitle("Entries")
    humH.GetYaxis().SetTitleOffset(2.1)

    peltVH = TH1D("PeltV", "RBX Peltier Voltages (V)", 20, minPV - 0.05, maxPV + 0.05)
    peltVH.SetFillColor(kCyan)
    peltVH.SetTitle("RBX Peltier Voltages (V)")
    peltVH.GetXaxis().SetTitle("Voltage (V)")
    peltVH.GetYaxis().SetTitle("Entries")
    peltVH.GetYaxis().SetTitleOffset(2.1)

    peltIH = TH1D("PeltI", "RBX Peltier Currents (A)", 20, minPI - 0.05, maxPI + 0.05)
    peltIH.SetFillColor(kGreen)
    peltIH.SetTitle("RBX Peltier Currents (A)")
    peltIH.GetXaxis().SetTitle("Current (A)")
    peltIH.GetYaxis().SetTitle("Entries")
    peltIH.GetYaxis().SetTitleOffset(2.1)

    leakIH = TH1D("LeakI", "RBX Leak Currents (A)", 20, minLI - 0.05, maxLI + 0.05)
    leakIH.SetFillColor(kOrange)
    leakIH.SetTitle("RBX Leakage Currents (mA)")
    leakIH.GetXaxis().SetTitle("Current (mA)")
    leakIH.GetYaxis().SetTitle("Entries")
    leakIH.GetYaxis().SetTitleOffset(2.0)
    leakIH.GetYaxis().SetTitleOffset(2.1)


    for i,entry in enumerate(readings):
	# Fill graphs
	for rm in range(len(entry["temp"])):
	    temp = entry["temp"][rm]
	    tempG[rm].SetPoint(i, i, temp)
	    tempH.Fill(temp)
	    
	for rm in range(len(entry["hum"])):
	    hum = entry["hum"][rm]
	    humG[rm].SetPoint(i, i, hum)
	    humH.Fill(hum)
	
	for rm in range(len(entry["peltV"])):
	    peltV = entry["peltV"][rm]
	    peltVG[rm].SetPoint(i, i, peltV)
	    peltVH.Fill(peltV)

	for rm in range(len(entry["peltI"])):
	    peltI = entry["peltI"][rm]
	    peltIG[rm].SetPoint(i, i, peltI)
	    peltIH.Fill(peltI)

	for qie in range(len(entry["leakI"])):
	    leakI = entry["leakI"][qie]
	    leakIH.Fill(leakI)
    
    plotMultiGraph(readings, tempG, "RBX Temperatures (^{o}C)", "Time", "Temp (^{o}C)", "Temp") 
    plotMultiGraph(readings, humG, "RBX Humidities (%)", "Time", "Humidity (%)", "Hum") 
    plotMultiGraph(readings, peltVG, "RBX Peltier Voltages (V)", "Time", "Voltage (V)", "PeltV") 
    plotMultiGraph(readings, peltIG, "RBX Peltier Currents (A)", "Time", "Current (A)", "PeltI") 
   
    plotHisto(tempH, "Temp")
    plotHisto(humH, "Hum")
    plotHisto(peltVH, "PeltV")
    plotHisto(peltIH, "PeltI")
    plotHisto(leakIH, "LeakI")


if __name__ == "__main__":
    sys.exit(main())
