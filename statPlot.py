#!/usr/bin/env python
########################################################################
#  statPlot.py							       #
#								       #
#  Parse an ngfec_auto log file and plots stats as a function of time  #
#								       #
#  Can specify min/max values to only print stats from particular log  #
#  entries. These values can be negative. For example, using min=-10   #
#  retrieves the last 10 entries. 				       #
#								       #
########################################################################

import sys
from argparse import ArgumentParser
import ROOT
from pprint import pprint
from ROOT import TGraph, TMultiGraph, TH1D, TLegend, TCanvas, TPad, gStyle, kRed, kBlue, kOrange, kCyan, kGreen, kBlack
ROOT.gROOT.SetBatch(True)

COLORS = [kRed, kCyan, kGreen, kBlack]
MARKERS = [21, 22, 29, 33] 

# Stat box contains
# e: entries
# m: mean
# r: rms
gStyle.SetOptStat("emr")
gStyle.SetStatW(0.16)
gStyle.SetStatX(1.0)
gStyle.SetStatY(0.9)


def plotMultiGraph(dataReadings, vals, title, xTitle, yTitle, outF):
    """
    Plots several TGraphs using TMultiGraph
    """
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
    cv.SaveAs(outF)


def plotHisto(histo, outF):    
    """
    Plots a (pre-initialized) histogram
    """
    cv = TCanvas(outF + "H", "cv", 1200, 1200)
    pad = TPad("p","p", 0.05, 0.0, 1.0, 1.0)
    pad.cd()
    histo.Draw("HIST")
    pad.Update()
    cv.cd()
    pad.Draw()
    cv.SaveAs(outF)


def main():
    parser = ArgumentParser()
    parser.add_argument("log", help="log file from ngfec_auto")
    parser.add_argument("--min", "-n", type=int, default=0, help="lower range bound (neg vals count backwards from the end)")
    parser.add_argument("--max", "-x", type=int, default=0, help="upper range bound (neg vals count backwards from the end")
    args = parser.parse_args()

    readings = []
    minT = 9999.0
    maxT = -9999.0
    minH = 101.0
    maxH = -1.0
   # # peltier voltage
    minPV = 9999.0
    maxPV = -9999.0
    # peltier current
    minPI = 9999.0
    maxPI = -9999.0
    # leakage current
    minLI = 9999.0
    maxLI = -9999.0
   
    # Count the number of lines in the log file
    lineCount = 0
    try:
	with open(args.log, "r") as fa:
	    for lineCount, line in enumerate(fa,1):    # Starts the counter at 1
		None
    except:
	print "Unable to open file:", args.log
	sys.exit()
    
    #print "Total lines:", lineCount 
    lineStart = args.min if args.min >= 0 else lineCount + args.min + 1
    lineEnd = args.max if args.max > 0 else lineCount + args.max + 1

    #print "lineStart =", lineStart
    #print "lineEnd =", lineEnd
    with open(args.log, "r") as f:
	for l, line in enumerate(f,1):
	    if lineStart <= l <= lineEnd:
		#print "Reading line", l
		data = line.split()
		entry = {}
		entry["date"] = data[0]
		entry["time"] = data[1]
		entry["temp"] = [float(data[i]) for i in xrange(2, 6)]
		entry["hum"]  = [float(data[i]) for i in xrange(6, 10)]
		entry["peltV"] = [float(data[i]) for i in xrange(10, 14)]
		entry["peltI"] = [float(data[i]) for i in xrange(14, 18)]
		try:
		    entry["leakI"] = [float(data[i]) for i in xrange(18, 210)]
		    minLI = min(minLI, min(entry["leakI"]))
		    maxLI = max(maxLI, max(entry["leakI"]))
		except:
		    # Read error with leakage currents
		    entry["leakI"] = []
		    minLI = 0
		    maxLI = 0

		minT = min(minT, min(entry["temp"]))
		maxT = max(maxT, max(entry["temp"]))
		minH = min(minH, min(entry["hum"]))
		maxH = max(maxH, max(entry["hum"]))
		minPV = min(minPV, min(entry["peltV"]))
		maxPV = max(maxPV, max(entry["peltV"]))
		minPI = min(minPI, min(entry["peltI"]))
		maxPI = max(maxPI, max(entry["peltI"]))
		readings.append(entry)

    tempG = []
    humG = []
    peltVG = []
    peltIG = []
    tempMG = TMultiGraph()
    humMG = TMultiGraph()
    peltVMG = TMultiGraph()
    peltIMG = TMultiGraph()


    # Initialize TGraphs
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

    # Book histograms
    widthT = 0.15 * (maxT - minT)   # Sets the spacing around a TH1D plot based on the max/min vals
    tempH = TH1D("Temp", "RBX Temperatures (^{o}C)", 20, minT - widthT, maxT + widthT)
    tempH.SetFillColor(kRed)
    tempH.SetTitle("RBX Temperatures (^{o}C)")
    tempH.GetXaxis().SetTitle("Temp (^{o}C)")
    tempH.GetYaxis().SetTitle("Entries")
    tempH.GetYaxis().SetTitleOffset(2.1)

   
    widthH = 0.15 * (maxH - minH)
    humH = TH1D("Humidity", "RBX Humidities (%)", 20, minH - widthH, maxH + widthH)
    humH.SetFillColor(kBlue)
    humH.SetTitle("RBX Humidities (%)")
    humH.GetXaxis().SetTitle("Humidity (%)")
    humH.GetYaxis().SetTitle("Entries")
    humH.GetYaxis().SetTitleOffset(2.1)

    widthPV = 0.15 * (maxPV - minPV)
    peltVH = TH1D("PeltV", "RBX Peltier Voltages (V)", 20, minPV - widthPV, maxPV + widthPV)
    peltVH.SetFillColor(kCyan)
    peltVH.SetTitle("RBX Peltier Voltages (V)")
    peltVH.GetXaxis().SetTitle("Voltage (V)")
    peltVH.GetYaxis().SetTitle("Entries")
    peltVH.GetYaxis().SetTitleOffset(2.1)

    widthPI = 0.15 * (maxPI - minPI)
    peltIH = TH1D("PeltI", "RBX Peltier Currents (A)", 20, minPI - widthPI, maxPI + widthPI)
    peltIH.SetFillColor(kGreen)
    peltIH.SetTitle("RBX Peltier Currents (A)")
    peltIH.GetXaxis().SetTitle("Current (A)")
    peltIH.GetYaxis().SetTitle("Entries")
    peltIH.GetYaxis().SetTitleOffset(2.1)

    widthLI = 0.15 * (maxLI - minLI)
    leakIH = TH1D("LeakI", "RBX Leak Currents (A)", 20, minLI - widthLI, maxLI + widthLI)
    leakIH.SetFillColor(kOrange)
    leakIH.SetTitle("RBX Leakage Currents (mA)")
    leakIH.GetXaxis().SetTitle("Current (mA)")
    leakIH.GetYaxis().SetTitle("Entries")
    leakIH.GetYaxis().SetTitleOffset(2.0)
    leakIH.GetYaxis().SetTitleOffset(2.1)


    # Fill graphs, histos
    for i,entry in enumerate(readings):
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
   
    # Make TMultiGraph plots
    plotMultiGraph(readings, tempG, "RBX Temperatures (^{o}C)", "Time", "Temp (^{o}C)", "plots/Temp_graph.png") 
    plotMultiGraph(readings, humG, "RBX Humidities (%)", "Time", "Humidity (%)", "plots/Hum_graph.png") 
    plotMultiGraph(readings, peltVG, "RBX Peltier Voltages (V)", "Time", "Voltage (V)", "plots/PeltV_graph.png") 
    plotMultiGraph(readings, peltIG, "RBX Peltier Currents (A)", "Time", "Current (A)", "plots/PeltI_graph.png") 
   
    # Make TH1D plots
    plotHisto(tempH, "plots/Temp_histo.png")
    plotHisto(humH, "plots/Hum_histo.png")
    plotHisto(peltVH, "plots/PeltV_histo.png")
    plotHisto(peltIH, "plots/PeltI_histo.png")
    plotHisto(leakIH, "plots/LeakI_histo.png")


if __name__ == "__main__":
    sys.exit(main())
