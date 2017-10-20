#!/usr/bin/env python
########################################################################
#  statPlot.py                                                         #
#                                                                      #
#  Parse an ngfec_auto log file and plots stats as a function of time  #
#                                                                      #
#  Can specify min/max values to only print stats from particular log  #
#  entries. These values can be negative. For example, using min=-10   #
#  retrieves the last 10 entries.                                      #
#                                                                      #
########################################################################

import sys
from argparse import ArgumentParser
import ROOT
from pprint import pprint
from ROOT import TGraph, TMultiGraph, TH1D, TLegend, TCanvas, TPad, gStyle, kRed, kBlue, kOrange, kCyan, kGreen, kBlack, kViolet, kMagenta
ROOT.gROOT.SetBatch(True)

#COLORS = [kRed, kCyan+1, kGreen+2, kViolet+1]
#MARKERS = [21, 22, 29, 33] 

COLORS = [kRed, kBlue, kOrange, kCyan, kGreen, kBlack, kViolet, kMagenta] 
COLORSprime = list(c+2 for c in COLORS)
COLORS = COLORS + COLORSprime
MARKERS = list(i for i in xrange(20,36))

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
    for a in xrange(len(vals)):
        print "vals[a] = {0}".format(vals[a])
        l.AddEntry(vals[a], "Value %d" % (a+1), "pl")
        mg.Add(vals[a])
    mg.Draw("alp")
    pad.Update()
    mg.SetTitle(title + ";" + xTitle + ";" + yTitle)
    l.Draw()
    cv.cd()
    pad.Draw()
    
    mg.GetXaxis().SetNdivisions(len(dataReadings))
    date = "" 
    nReadings = len(dataReadings)
    divisor = nReadings / 10 + 1 # use to label no more than 10 bins, include first and last bins always
    for i in xrange(nReadings):
        if i % divisor == 0 or i == nReadings - 1:
            # If new date, print date and time
            if date != dataReadings[i]["date"]:
                date = dataReadings[i]["date"]
                mg.GetXaxis().SetBinLabel(mg.GetXaxis().FindBin(i), "#splitline{%s}{%s}"%(date, dataReadings[i]["time"]))
            else:
                mg.GetXaxis().SetBinLabel(mg.GetXaxis().FindBin(i), dataReadings[i]["time"])

    mg.GetXaxis().SetTitleOffset(2.1)
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
    parser.add_argument("--max", "-x", type=int, default=0, help="upper range bound (neg vals count backwards from the end)")
    parser.add_argument("--out", "-o", default="plots/", help="directory to save plots in")
    args = parser.parse_args()
    
    #variables = ["temp", "hum", "peltV", "peltI", "BVin", "Vin", "leakI"]
    variables = ["temps", "hums", "peltV", "peltI", "BVin", "Vin", "leakI", "cardT", "calibT", "setV", "targetT"]
    
    if args.out[-1] != "/":
        args.out += "/"
    readings = []
    varMins = {}
    varMaxs = {}
    for v in variables:
        varMins[v] = 9999.0 
        varMaxs[v] = -9999.0 
    '''
    # temperature
    minT = 9999.0
    maxT = -9999.0
    # humidity
    minH = 101.0
    maxH = -1.0
    # peltier voltage
    minPV = 9999.0
    maxPV = -9999.0
    # peltier current
    minPI = 9999.0
    maxPI = -9999.0
    # BVin
    minBVin = 9999.0
    maxBVin = -9999.0
    # Vin
    minVin = 9999.0
    maxVin = -9999.0
    # leakage current
    minLI = 9999.0
    maxLI = -9999.0
    # RM temperature
    minTRM = 9999.0
    maxTRM = -9999.0
    # CU temperature
    minTCU = 9999.0
    maxTCU = -9999.0
    # RM humidity
    minHRM = 101.0
    maxHRM = -1.0
    # CU humidity
    minHCU = 101.0
    maxHCU = -1.0
    # RTD temperature
    minTRTD = 9999.0
    maxTRTD = -9999.0
    ''' 
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
    # HE has 48 channels per RM
    # HB has 64 channels per RM
    nRMchs = 64
    nRMs = 4
    #params = ["temp", "hum", "peltV", "peltI", "BVin", "Vin"]
    with open(args.log, "r") as f:
        for l, line in enumerate(f,1):
            if lineStart <= l <= lineEnd:
                data = line.split()
                print "Reading line %d with %d data values" % (l, len(data))
                entry = {}
                entry["date"] = data[0]
                entry["time"] = data[1]
                n = 2
                for v in variables:
                    print "v: {0} n: {1}".format(v, n)
                    if v == "leakI":
                        # we need to update this try because leakage currents are not read last right now...
                        try:
                            entry[v] = [float(data[i]) for i in xrange(n, n + nRMs * nRMchs)]
                            n += nRMs * nRMchs
                        except:
                            # Read error with leakage currents
                            entry["leakI"] = []
                    elif v in ["cardT"]:
                        entry[v] = [float(data[i]) for i in xrange(n, n + 4 * nRMs)]
                        n += 4 * nRMs
                    elif v in ["calibT"]:
                        entry[v] = [float(data[i]) for i in xrange(n, n + 1)]
                        n += 1
                    else: 
                        entry[v] = [float(data[i]) for i in xrange(n, n + nRMs)]
                        n += nRMs
                    
                    varMins[v] = min(varMins[v], min(entry[v]))
                    varMaxs[v] = max(varMaxs[v], max(entry[v]))

                '''
                entry[p] = [float(data[i]) for i in xrange(2, 6)]
                entry[p] = [float(data[i]) for i in xrange(6, 10)]
                entry[p] = [float(data[i]) for i in xrange(10, 14)]
                entry[p] = [float(data[i]) for i in xrange(14, 18)]
                entry[p] = [float(data[i]) for i in xrange(18, 22)]
                entry[p] = [float(data[i]) for i in xrange(22, 26)]
                
                minT = min(minT, min(entry["temp"]))
                maxT = max(maxT, max(entry["temp"]))
                minH = min(minH, min(entry["hum"]))
                maxH = max(maxH, max(entry["hum"]))
                minPV = min(minPV, min(entry["peltV"]))
                maxPV = max(maxPV, max(entry["peltV"]))
                minPI = min(minPI, min(entry["peltI"]))
                maxPI = max(maxPI, max(entry["peltI"]))         
                minBVin = min(minBVin, min(entry["BVin"]))
                maxBVin = max(maxBVin, max(entry["BVin"]))
                minVin = min(minVin, min(entry["Vin"]))
                maxVin = max(maxVin, max(entry["Vin"]))
                minTRM = min(minTRM, min(entry["tempRM"]))
                maxTRM = min(maxTRM, min(entry["tempRM"]))
                minTCU = min(minTCU, min(entry["tempCU"]))
                maxTCU = min(maxTCU, min(entry["tempCU"]))
                minHRM = min(minHRM, min(entry["humRM"]))
                maxHRM = min(maxHRM, min(entry["humRM"]))
                minHCU = min(minHCU, min(entry["humCU"]))
                maxHCU = min(maxHCU, min(entry["humCU"]))
                minTRTD = min(minTRTD, min(entry["tempRTD"]))
                maxTRTD = min(maxTRTD, min(entry["tempRTD"]))
                '''
                readings.append(entry)

    '''
    tempG = []
    humG = []
    peltVG = []
    peltIG = []
    BVinG = []
    VinG = []
    
    tempMG = TMultiGraph()
    humMG = TMultiGraph()
    peltVMG = TMultiGraph()
    peltIMG = TMultiGraph()
    BVinMG = TMultiGraph()
    VinMG = TMultiGraph()
    '''
    
    # Initialize TGraphs
    graphs = {}
    for v in variables:
        graphs[v] = []
        if v != "leakI":
            for i in xrange(len(readings[0][v])):
                print "Create graphs for variable: %s i: %d" % (v, i)
                graphs[v].append(TGraph())
                graphs[v][i].SetLineColor(COLORS[i])
                graphs[v][i].SetLineWidth(2)
                graphs[v][i].SetMarkerStyle(MARKERS[i])
                graphs[v][i].SetMarkerSize(2)
                graphs[v][i].SetMarkerColor(COLORS[i])

    '''
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
    
    for i in range(len(readings[0]["BVin"])):
        BVinG.append(TGraph())
        BVinG[i].SetLineColor(COLORS[i])
        BVinG[i].SetLineWidth(2)
        BVinG[i].SetMarkerStyle(MARKERS[i])
        BVinG[i].SetMarkerSize(2)
        BVinG[i].SetMarkerColor(COLORS[i])

    for i in range(len(readings[0]["Vin"])):
        VinG.append(TGraph())
        VinG[i].SetLineColor(COLORS[i])
        VinG[i].SetLineWidth(2)
        VinG[i].SetMarkerStyle(MARKERS[i])
        VinG[i].SetMarkerSize(2)
        VinG[i].SetMarkerColor(COLORS[i])
    '''

    titles = {} # name, title, x-axis unit, y-axis unit
    titles["temps"]  = ["Temp",      "Peltier Temperature (^{o}C)",  "Temp (^{o}C)",     "Entries"]
    titles["hums"]   = ["Humidity",  "Peltier Humidity (%)",         "Humidity (%)",     "Entries"]
    titles["peltV"]  = ["PeltV",     "Peltier Voltage (V)",          "Voltage (V)",      "Entries"]
    titles["peltI"]  = ["PeltI",     "Peltier Current (A)",          "Current (A)",      "Entries"]
    titles["BVin"]   = ["BVin",      "Bulk Bias Voltage (V)",        "Voltage (V)",      "Entries"]
    titles["Vin"]    = ["Vin",       "Backplane Voltage (V)",        "Voltage (V)",      "Entries"]
    titles["leakI"]  = ["LeakI",     "SiPM Leakage Current (\muA)",  "Current (\mA)",    "Entries"]
    titles["cardT"]  = ["CardTemp",  "RM QIE Card Temperature (^{o}C)", "Temp (^{o}C)",     "Entries"]
    titles["calibT"] = ["CalibTemp", "CU QIE Card Temperature (^{o}C)", "Temp (^{o}C)",     "Entries"]
    titles["setV"]   = ["SetV",      "Set Peltier Voltage (V)",      "Voltage (V)",      "Entries"]
    titles["targetT"] = ["TargetTemp", "Peltier Target Temperature (^{o}C)", "Temp (^{o}C)", "Entries"]
    
    histograms = {}
    j = 0
    for v in variables:
        width = 0.15 * (varMaxs[v] - varMins[v])   # Sets the spacing around a TH1D plot based on the max/min vals
        histograms[v] = TH1D(titles[v][0], titles[v][1], 50, varMins[v] - width, varMaxs[v] + width)
        histograms[v].SetFillColor(COLORS[j])
        histograms[v].GetXaxis().SetTitle(titles[v][2])
        histograms[v].GetYaxis().SetTitle(titles[v][3])
        histograms[v].GetYaxis().SetTitleOffset(2.1)
        j += 1
    
    '''
    # Book histograms
    widthT = 0.15 * (varMaxs["temp"] - varMins["temp"])   # Sets the spacing around a TH1D plot based on the max/min vals
    tempH = TH1D("Temp", "RBX Temperature (^{o}C)", 50, varMins["temp"] - widthT, varMaxs["temp"] + widthT)
    tempH.SetFillColor(kRed)
    tempH.GetXaxis().SetTitle("Temp (^{o}C)")
    tempH.GetYaxis().SetTitle("Entries")
    tempH.GetYaxis().SetTitleOffset(2.1)

   
    widthT = 0.15 * (varMaxs["hum"] - varMins["hum"])   # Sets the spacing around a TH1D plot based on the max/min vals
    humH = TH1D("Humidity", "RBX Humidity (%)", 50, varMins["hum"] - widthH, varMaxs["hum"] + widthH)
    humH.SetFillColor(kBlue)
    humH.GetXaxis().SetTitle("Humidity (%)")
    humH.GetYaxis().SetTitle("Entries")
    humH.GetYaxis().SetTitleOffset(2.1)

    widthPV = 0.15 * (maxPV - minPV)
    peltVH = TH1D("PeltV", "RBX Peltier Voltage (V)", 50, minPV - widthPV, maxPV + widthPV)
    peltVH.SetFillColor(kCyan+1)
    peltVH.GetXaxis().SetTitle("Voltage (V)")
    peltVH.GetYaxis().SetTitle("Entries")
    peltVH.GetYaxis().SetTitleOffset(2.1)

    widthPI = 0.15 * (maxPI - minPI)
    peltIH = TH1D("PeltI", "RBX Peltier Current (A)", 50, minPI - widthPI, maxPI + widthPI)
    peltIH.SetFillColor(kGreen+2)
    peltIH.GetXaxis().SetTitle("Current (A)")
    peltIH.GetYaxis().SetTitle("Entries")
    peltIH.GetYaxis().SetTitleOffset(2.1)

    widthBVin = 0.15 * (maxBVin - minBVin)
    BVinH = TH1D("BVinH", "RBX Bulk Bias Voltage In (V)", 50, minBVin - widthBVin, maxBVin + widthBVin)
    BVinH.SetFillColor(kViolet+1)
    BVinH.GetXaxis().SetTitle("Voltage (V)")
    BVinH.GetYaxis().SetTitle("Entries")
    BVinH.GetYaxis().SetTitleOffset(2.1)
    
    widthVin = 0.15 * (maxVin - minVin)
    VinH = TH1D("VinH", "RBX Backplane Voltage In (V)", 50, minVin - widthVin, maxVin + widthVin)
    VinH.SetFillColor(kMagenta)
    VinH.GetXaxis().SetTitle("Voltage (V)")
    VinH.GetYaxis().SetTitle("Entries")
    VinH.GetYaxis().SetTitleOffset(2.1)
    
    widthLI = 0.15 * (maxLI - minLI)
    leakIH = TH1D("LeakI", "SiPM Leakage Current (\muA)", 50, minLI - widthLI, maxLI + widthLI)
    leakIH.SetFillColor(kOrange)
    leakIH.GetXaxis().SetTitle("Current (\muA)")
    leakIH.GetYaxis().SetTitle("Entries")
    leakIH.GetYaxis().SetTitleOffset(2.0)
    leakIH.GetYaxis().SetTitleOffset(2.1)
    '''

    # Fill graphs, histos
    for i,entry in enumerate(readings):
        for v in variables:
            for a in xrange(len(entry[v])):
                value = entry[v][a]
                histograms[v].Fill(value)
                if v != "leakI":
                    graphs[v][a].SetPoint(i, i, value)
            
        '''
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

        for rm in range(len(entry["BVin"])):
            BVin = entry["BVin"][rm]
            BVinG[rm].SetPoint(i, i, BVin)
            BVinH.Fill(BVin)
        
        for rm in range(len(entry["Vin"])):
            Vin = entry["Vin"][rm]
            VinG[rm].SetPoint(i, i, Vin)
            VinH.Fill(Vin)
  
        for qie in range(len(entry["leakI"])):
            leakI = entry["leakI"][qie]
            leakIH.Fill(leakI)
        '''

    for v in variables:
        # Make TH1D plots
        plotHisto(histograms[v], "plots/%s_histo.png" % titles[v][0])
        # Make TMultiGraph plots
        if v != "leakI":
            plotMultiGraph(readings, graphs[v], titles[v][1], "Time", titles[v][2], "plots/%s_graph.png" % titles[v][0]) 

    ''' 
    plotMultiGraph(readings, graphs["temp"],    "RBX Temperature (^{o}C)",      "Time", "Temp (^{o}C)", "plots/Temp_graph.png") 
    plotMultiGraph(readings, graphs["hum"],     "RBX Humidity (%)",             "Time", "Humidity (%)", "plots/Hum_graph.png") 
    plotMultiGraph(readings, graphs["peltV"],   "RBX Peltier Voltage (V)",      "Time", "Voltage (V)",  "plots/PeltV_graph.png") 
    plotMultiGraph(readings, graphs["peltI"],   "RBX Peltier Current (A)",      "Time", "Current (A)",  "plots/PeltI_graph.png")
    plotMultiGraph(readings, graphs["BVin"],    "RBX Bulk Bias Voltage In (V)", "Time", "Voltage (V)",  "plots/BVin_graph.png") 
    plotMultiGraph(readings, graphs["Vin"],     "RBX Backplane Voltage In (V)", "Time", "Voltage (V)",  "plots/Vin_graph.png") 

    # Make TH1D plots
    plotHisto(tempH,    "plots/Temp_histo.png")
    plotHisto(humH,     "plots/Hum_histo.png")
    plotHisto(peltVH,   "plots/PeltV_histo.png")
    plotHisto(peltIH,   "plots/PeltI_histo.png")
    plotHisto(BVinH,    "plots/BVin_histo.png")
    plotHisto(VinH,     "plots/Vin_histo.png") 
    plotHisto(leakIH,   "plots/LeakI_histo.png")
    '''

if __name__ == "__main__":
    sys.exit(main())
